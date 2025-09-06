import numpy as np
import itertools
from typing import Any, Dict, List, Optional, Tuple
import qutip as qt

from .utils.file_io import Serializable
from .utils.parallel import parallel_map
from .displaced_state import DisplacedState
from .model import Model
from .options import Options


class FloquetAnalysis(Serializable):
    """Perform a floquet analysis to identify nonlinear resonances.

    In most workflows, one needs only to call the run() method which performs
    both the displaced state fit and the Blais branch analysis. For an example
    workflow, see the [transmon](../examples/transmon) tutorial.

    Arguments:
        model: Class specifying the model, including the Hamiltonian, drive amplitudes,
            frequencies
        state_indices: State indices of interest. Defaults to [0, 1], indicating the two
            lowest-energy states.
        options: Options for the Floquet analysis.
        init_data_to_save: Initial parameter metadata to save to file. Defaults to None.
    """

    def __init__(self, model, state_indices=None, options=None, init_data_to_save=None):
        """Initialize an instance of the class with a model, state indices, options, and initial data to save, setting default values if not provided."""
        self.model = model
        self.state_indices = state_indices if state_indices is not None else [0, 1]
        self.options = options if options is not None else Options()
        self.init_data_to_save = init_data_to_save
        self.hilbert_dim = self.model.H0.shape[0]

    def __str__(self):
        """Return a formatted string representation of the Floquet simulation parameters, including the base class's string representation."""
        base_str = super().__str__()
        return f"FloquetAnalysis:\n{base_str}"

    def bare_state_array(self):
        """Return array of bare states.

        Used to specify initial bare states for the Blais branch analysis.
        """
        bare_states = np.zeros((len(self.state_indices), self.hilbert_dim), dtype=complex)
        for i, state_idx in enumerate(self.state_indices):
            bare_states[i, state_idx] = 1.0
        return bare_states

    def run_one_floquet(self, omega_d_amp):
        """Run one instance of the problem for a pair of drive frequency and amp.

        Returns floquet modes as numpy column vectors, as well as the quasienergies.

        Parameters:
            omega_d_amp: Pair of drive frequency and amp.
        """
        omega_d, amp = omega_d_amp
        H = self.model.hamiltonian((omega_d, amp))
        
        T = 2 * np.pi / omega_d
        tlist = np.array([self.options.floquet_sampling_time_fraction * T])
        
        f_modes, f_energies = qt.floquet_modes(H, T, tlist, options={'nsteps': self.options.nsteps})
        
        f_modes_array = np.zeros((len(f_modes), self.hilbert_dim), dtype=complex)
        for i, mode in enumerate(f_modes):
            f_modes_array[i] = mode.full().flatten()
        
        return f_modes_array, f_energies

    def _calculate_mean_excitation(self, f_modes_ordered):
        """Mean excitation number of ordered floquet modes.

        Based on Blais arXiv:2402.06615, specifically Eq. (12) but going without the
        integral over floquet modes in one period.
        """
        mean_excitations = np.zeros(len(f_modes_ordered))
        
        for i, mode in enumerate(f_modes_ordered):
            n_op = qt.num(self.hilbert_dim)
            mean_excitations[i] = qt.expect(n_op, qt.Qobj(mode))
        
        return mean_excitations

    def _step_in_amp(self, f_modes_energies, prev_f_modes):
        """Perform Blais branch analysis.

        Gorgeous in its simplicity. Simply calculate overlaps of new floquet modes with
        those from the previous amplitude step, and order the modes accordingly. So
        ordered, compute the mean excitation number, yielding our branches.
        """
        f_modes, f_energies = f_modes_energies
        
        overlaps = np.zeros((len(f_modes), len(prev_f_modes)))
        for i, new_mode in enumerate(f_modes):
            for j, prev_mode in enumerate(prev_f_modes):
                overlaps[i, j] = np.abs(np.vdot(new_mode, prev_mode))
        
        ordering = np.argmax(overlaps, axis=1)
        f_modes_ordered = f_modes[ordering]
        f_energies_ordered = f_energies[ordering]
        
        mean_excitations = self._calculate_mean_excitation(f_modes_ordered)
        
        return f_modes_ordered, f_energies_ordered, mean_excitations

    def _place_into(self, amp_idxs, array_for_range, overall_array):
        """Place a specified range of values from `array_for_range` into a corresponding range in `overall_array` as defined by the indices in `amp_idxs`."""
        overall_array[amp_idxs[0]:amp_idxs[1]] = array_for_range
        return overall_array

    def identify_floquet_modes(self, f_modes_energies, params_0, displaced_state, previous_coefficients):
        """Return floquet modes with largest overlap with ideal displaced state.

        Also return that overlap value.

        Parameters:
            f_modes_energies: output of self.run_one_floquet(params)
            params_0: (omega_d_0, amp_0) to use for displaced fit
            displaced_state: Instance of DisplacedState
            previous_coefficients: Coefficients from the previous amplitude range that
                will be used when calculating overlap of the floquet modes against
                the 'bare' states specified by previous_coefficients
        """
        f_modes, f_energies = f_modes_energies
        omega_d_0, amp_0 = params_0
        
        overlaps = np.zeros((len(f_modes), len(self.state_indices)))
        for i, mode in enumerate(f_modes):
            for j, state_idx in enumerate(self.state_indices):
                bare_state = displaced_state.displaced_state(omega_d_0, amp_0, state_idx, previous_coefficients[j])
                overlaps[i, j] = np.abs(np.vdot(mode, bare_state))
        
        best_modes = []
        best_overlaps = []
        for j in range(len(self.state_indices)):
            best_idx = np.argmax(overlaps[:, j])
            best_modes.append(f_modes[best_idx])
            best_overlaps.append(overlaps[best_idx, j])
        
        return np.array(best_modes), np.array(best_overlaps)

    def _floquet_main_for_amp_range(self, amp_idxs, displaced_state, previous_coefficients, prev_f_modes_arr):
        """Run the floquet simulation over a specific amplitude range."""
        num_omega_d = len(self.model.omega_d_values)
        num_amp = amp_idxs[1] - amp_idxs[0]
        
        f_modes_arr = np.zeros((num_omega_d, num_amp, len(self.state_indices), self.hilbert_dim), dtype=complex)
        f_energies_arr = np.zeros((num_omega_d, num_amp, len(self.state_indices)), dtype=float)
        overlaps_arr = np.zeros((num_omega_d, num_amp, len(self.state_indices)), dtype=float)
        mean_excitations_arr = np.zeros((num_omega_d, num_amp, len(self.state_indices)), dtype=float)
        
        omega_d_amp_params = self.model.omega_d_amp_params(amp_idxs)
        
        all_results = list(parallel_map(
            self.run_one_floquet,
            omega_d_amp_params,
            self.options.num_cpus
        ))
        
        results_idx = 0
        for omega_d_idx, omega_d in enumerate(self.model.omega_d_values):
            for amp_idx in range(num_amp):
                actual_amp_idx = amp_idxs[0] + amp_idx
                amp = self.model.drive_amplitudes[omega_d_idx][actual_amp_idx]
                
                f_modes, f_energies = all_results[results_idx]
                results_idx += 1
                
                if prev_f_modes_arr is not None:
                    prev_f_modes = prev_f_modes_arr[omega_d_idx, amp_idx - 1 if amp_idx > 0 else 0]
                    f_modes_ordered, f_energies_ordered, mean_excitations = self._step_in_amp(
                        (f_modes, f_energies), prev_f_modes
                    )
                else:
                    f_modes_ordered = f_modes
                    f_energies_ordered = f_energies
                    mean_excitations = self._calculate_mean_excitation(f_modes_ordered)
                
                best_modes, best_overlaps = self.identify_floquet_modes(
                    (f_modes_ordered, f_energies_ordered),
                    (omega_d, amp),
                    displaced_state,
                    previous_coefficients
                )
                
                f_modes_arr[omega_d_idx, amp_idx] = best_modes
                f_energies_arr[omega_d_idx, amp_idx] = f_energies_ordered[:len(self.state_indices)]
                overlaps_arr[omega_d_idx, amp_idx] = best_overlaps
                mean_excitations_arr[omega_d_idx, amp_idx] = mean_excitations[:len(self.state_indices)]
        
        return f_modes_arr, f_energies_arr, overlaps_arr, mean_excitations_arr

    def run(self, filepath):
        """Perform floquet analysis over range of amplitudes and drive frequencies.

        This function largely performs two calculations. The first is the Xiao analysis
        introduced in https://arxiv.org/abs/2304.13656, fitting the extracted Floquet
        modes to the "ideal" displaced state which does not include resonances by design
        (because we fit to a low order polynomial and ignore any floquet modes with
        overlap with the bare state below a given threshold). This analysis produces the
        "scar" plots. The second is the Blais branch analysis, which tracks the Floquet
        modes by stepping in drive amplitude for a given drive frequency. For this
        reason the code is structured to parallelize over drive frequency, but scans in
        a loop over drive amplitude. This way the two calculations can be performed
        simultaneously.

        A nice bonus is that both of the above mentioned calculations determine
        essentially independently whether a resonance occurs. In the first, it is
        deviation of the Floquet mode from the fitted displaced state. In the second,
        it is branch swapping that indicates a resonance, independent of any fit. Thus
        the two simulations can be used for cross validation of one another.

        We perform these simulations iteratively over the drive amplitudes as specified
        by fit_range_fraction. This is to allow for simulations stretching to large
        drive amplitudes, where the overlap with the bare eigenstate would fall below
        the threshold (due to ac Stark shift) even in the absence of any resonances.
        We thus use the fit from the previous range of drive amplitudes as our new bare
        state.
        """
        displaced_state = DisplacedState(
            self.hilbert_dim, self.model, self.state_indices, self.options
        )
        
        num_amp_total = len(self.model.drive_amplitudes[0])
        range_size = int(num_amp_total * self.options.fit_range_fraction)
        
        all_f_modes = np.zeros((len(self.model.omega_d_values), num_amp_total, len(self.state_indices), self.hilbert_dim), dtype=complex)
        all_f_energies = np.zeros((len(self.model.omega_d_values), num_amp_total, len(self.state_indices)), dtype=float)
        all_overlaps = np.zeros((len(self.model.omega_d_values), num_amp_total, len(self.state_indices)), dtype=float)
        all_mean_excitations = np.zeros((len(self.model.omega_d_values), num_amp_total, len(self.state_indices)), dtype=float)
        
        coefficients = np.zeros((len(self.state_indices), len(displaced_state.exponent_pair_idx_map)))
        prev_f_modes_arr = None
        
        for i in range(0, num_amp_total, range_size):
            amp_idxs = [i, min(i + range_size, num_amp_total)]
            
            if i == 0:
                previous_coefficients = [displaced_state.bare_state_coefficients(idx) for idx in self.state_indices]
            else:
                previous_coefficients = coefficients
            
            f_modes_arr, f_energies_arr, overlaps_arr, mean_excitations_arr = self._floquet_main_for_amp_range(
                amp_idxs, displaced_state, previous_coefficients, prev_f_modes_arr
            )
            
            all_f_modes = self._place_into(amp_idxs, f_modes_arr, all_f_modes)
            all_f_energies = self._place_into(amp_idxs, f_energies_arr, all_f_energies)
            all_overlaps = self._place_into(amp_idxs, overlaps_arr, all_overlaps)
            all_mean_excitations = self._place_into(amp_idxs, mean_excitations_arr, all_mean_excitations)
            
            omega_d_amp_slice = []
            for omega_d_idx, omega_d in enumerate(self.model.omega_d_values):
                for amp_idx in range(amp_idxs[0], amp_idxs[1]):
                    amp = self.model.drive_amplitudes[omega_d_idx][amp_idx]
                    omega_d_amp_slice.append((omega_d, amp))
            
            coefficients = displaced_state.displaced_states_fit(
                omega_d_amp_slice, all_overlaps[:, amp_idxs[0]:amp_idxs[1]], all_f_modes[:, amp_idxs[0]:amp_idxs[1]]
            )
            
            prev_f_modes_arr = all_f_modes[:, amp_idxs[1] - 1]
        
        data_to_save = {
            'f_modes': all_f_modes if self.options.save_floquet_modes else None,
            'f_energies': all_f_energies,
            'overlaps': all_overlaps,
            'mean_excitations': all_mean_excitations,
            'coefficients': coefficients
        }
        
        if self.init_data_to_save:
            data_to_save.update(self.init_data_to_save)
        
        self.write_to_file(filepath, data_to_save)
        
        return data_to_save