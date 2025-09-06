import numpy as np
from scipy.optimize import curve_fit
from typing import Any, Dict, List, Tuple
import itertools

from ..utils.file_io import Serializable
from ..model import Model
from ..options import Options


class DisplacedState(Serializable):
    """Class providing methods for computing displaced states.

    Parameters:
        hilbert_dim: Hilbert space dimension
        model: Model including the Hamiltonian, drive amplitudes, frequencies,
            state indices
        state_indices: States of interest
        options: Options used
    """

    def __init__(self, hilbert_dim, model, state_indices, options):
        """Initialize an instance of the class with the specified Hilbert dimension, model, state indices, and options, and create a mapping for exponent pairs."""
        self.hilbert_dim = hilbert_dim
        self.model = model
        self.state_indices = state_indices
        self.options = options
        self.exponent_pair_idx_map = self._create_exponent_pair_idx_map()

    def _create_exponent_pair_idx_map(self):
        """Create dictionary of terms in polynomial that we fit.

        We truncate the fit if e.g. there is only a single frequency value to scan over
        but the fit is nominally set to order four. We additionally eliminate the
        constant term that should always be either zero or one.
        """
        exponent_pairs = []
        for i in range(self.options.fit_cutoff + 1):
            for j in range(self.options.fit_cutoff + 1):
                if i + j <= self.options.fit_cutoff and (i, j) != (0, 0):
                    exponent_pairs.append((i, j))
        
        return {pair: idx for idx, pair in enumerate(exponent_pairs)}

    def _coefficient_for_state(self, xydata, state_idx_coefficients, bare_same):
        """Fit function to pass to curve fit, assume a 2D polynomial."""
        omega_d, amp = xydata
        result = 0.0
        
        for (i, j), idx in self.exponent_pair_idx_map.items():
            if bare_same:
                if (i, j) == (0, 0):
                    result += 1.0
                else:
                    result += 0.0
            else:
                result += state_idx_coefficients[idx] * (omega_d ** i) * (amp ** j)
        
        return result

    def _fit_coefficients_factory(self, XYdata, Zdata, p0, bare_same):
        """Fit polynomial coefficients to given XY and Z data using curve fitting, with fallback to zero coefficients if fitting fails."""
        try:
            popt, _ = curve_fit(
                lambda xydata, *coeffs: self._coefficient_for_state(
                    xydata, coeffs, bare_same
                ),
                XYdata,
                Zdata,
                p0=p0
            )
            return popt
        except (RuntimeError, ValueError):
            return np.zeros(len(p0))

    def _fit_coefficients_for_component(self, omega_d_amp_filtered, floquet_component_filtered, bare_same):
        """Fit the floquet modes to an "ideal" displaced state based on a polynomial.

        This is done here over the grid specified by omega_d_amp_slice. We ignore
        floquet mode data indicated by mask, where we suspect by looking at overlaps
        with the bare state that we have hit a resonance.
        """
        XYdata = np.array(omega_d_amp_filtered).T
        Zdata = floquet_component_filtered
        
        p0 = np.zeros(len(self.exponent_pair_idx_map))
        return self._fit_coefficients_factory(XYdata, Zdata, p0, bare_same)

    def bare_state_coefficients(self, state_idx):
        """For bare state only component is itself.

        Parameters:
            state_idx: Coefficients for the state $|state_idx\\rangle$ that when
                evaluated at any amplitude or frequency simply return the bare state.
                Note that this should be the actual state index, and not the array index
                (for instance if we have state_indices=[0, 1, 3] because we're not
                interested in the second excited state, for the 3rd excited state we
                should pass 3 here and not 2).
        """
        coefficients = np.zeros(len(self.exponent_pair_idx_map))
        return coefficients

    def displaced_states_fit(self, omega_d_amp_slice, ovlp_with_bare_states, floquet_modes):
        """Perform a fit for the indicated range, ignoring specified modes.

        We loop over all states in state_indices and perform the fit for a given
        amplitude range. We ignore floquet modes (not included in the fit) where
        the corresponding value in ovlp_with_bare_states is below the threshold
        specified in options.

        Parameters:
            omega_d_amp_slice: Pairs of omega_d, amplitude values at which the
                floquet modes have been computed and which we will use as the
                independent variables to fit the Floquet modes
            ovlp_with_bare_states: Bare state overlaps that has shape (w, a, s) where w
                is drive frequency, a is drive amplitude and s is state_indices
            floquet_modes: Floquet mode array with the same shape as
                ovlp_with_bare_states except with an additional trailing dimension h,
                the Hilbert-space dimension.

        Returns:
            Optimized fit coefficients
        """
        coefficients = np.zeros((len(self.state_indices), len(self.exponent_pair_idx_map)))
        
        for state_idx_idx, state_idx in enumerate(self.state_indices):
            mask = ovlp_with_bare_states[:, :, state_idx_idx] >= self.options.overlap_cutoff
            
            omega_d_amp_filtered = []
            floquet_component_filtered = []
            
            for i, (omega_d, amp) in enumerate(omega_d_amp_slice):
                if mask.flat[i]:
                    omega_d_amp_filtered.append((omega_d, amp))
                    floquet_component_filtered.append(floquet_modes.flat[i][state_idx])
            
            if len(omega_d_amp_filtered) > 0:
                coefficients[state_idx_idx] = self._fit_coefficients_for_component(
                    omega_d_amp_filtered, floquet_component_filtered, False
                )
        
        return coefficients

    def displaced_state(self, omega_d, amp, state_idx, coefficients):
        """Construct the ideal displaced state based on a polynomial expansion."""
        state_vector = np.zeros(self.hilbert_dim, dtype=complex)
        state_vector[state_idx] = 1.0
        
        for (i, j), idx in self.exponent_pair_idx_map.items():
            state_vector += coefficients[idx] * (omega_d ** i) * (amp ** j) * state_vector
        
        return state_vector

    def overlap_with_bare_states(self, amp_idx_0, coefficients, floquet_modes):
        """Calculate overlap of floquet modes with 'bare' states.

        'Bare' here is defined loosely. For the first range of amplitudes, the bare
        states are truly the bare states (the coefficients are obtained from
        bare_state_coefficients, which give the bare states). For later ranges, we
        define the bare state as the state obtained from the fit from previous range,
        with amplitude evaluated at the lower edge of amplitudes for the new region.
        This is, in a sense, the most natural choice, since it is most analogous to what
        is done in the first window when the overlap is computed against bare
        eigenstates (that obviously don't have amplitude dependence). Moreover, the fit
        coefficients for the previous window by definition were obtained in a window
        that does not include the one we are currently investigating. Asking for the
        state with amplitude values outside of the fit window should be done at your
        own peril.

        Parameters:
            amp_idx_0: Index specifying the lower bound of the amplitude range.
            coefficients: coefficients that specify the bare state that we calculate
                overlaps of Floquet modes against
            floquet_modes: Floquet modes to be compared to the bare states given by
                coefficients
        Returns:
            overlaps with shape (w,a,s) where w is the number of drive frequencies,
                a is the number of drive amplitudes (specified by amp_idxs) and s is the
                number of states we are investigating
        """
        num_omega_d = len(self.model.omega_d_values)
        num_amp = floquet_modes.shape[1]
        num_states = len(self.state_indices)
        
        overlaps = np.zeros((num_omega_d, num_amp, num_states), dtype=complex)
        
        for omega_d_idx, omega_d in enumerate(self.model.omega_d_values):
            for amp_idx in range(num_amp):
                amp = self.model.drive_amplitudes[omega_d_idx][amp_idx_0 + amp_idx]
                
                for state_idx_idx, state_idx in enumerate(self.state_indices):
                    bare_state = self.displaced_state(omega_d, amp, state_idx, coefficients[state_idx_idx])
                    floquet_mode = floquet_modes[omega_d_idx, amp_idx, state_idx_idx]
                    
                    overlap = np.vdot(bare_state, floquet_mode)
                    overlaps[omega_d_idx, amp_idx, state_idx_idx] = overlap
        
        return np.abs(overlaps)

    def overlap_with_displaced_states(self, amp_idxs, coefficients, floquet_modes):
        """Calculate overlap of floquet modes with 'ideal' displaced states.

        This is done here for a specific amplitude range.

        Parameters:
            amp_idxs: list of lower and upper amplitude indices specifying the range of
                drive amplitudes this calculation should be done for
            coefficients: coefficients that specify the displaced state that we
                calculate overlaps of Floquet modes against
            floquet_modes: Floquet modes to be compared to the displaced states given by
                coefficients
        Returns:
            overlaps with shape (w,a,s) where w is the number of drive frequencies,
                a is the number of drive amplitudes (specified by amp_idxs) and s is the
                number of states we are investigating
        """
        num_omega_d = len(self.model.omega_d_values)
        num_amp = amp_idxs[1] - amp_idxs[0]
        num_states = len(self.state_indices)
        
        overlaps = np.zeros((num_omega_d, num_amp, num_states), dtype=complex)
        
        for omega_d_idx, omega_d in enumerate(self.model.omega_d_values):
            for amp_idx in range(num_amp):
                actual_amp_idx = amp_idxs[0] + amp_idx
                amp = self.model.drive_amplitudes[omega_d_idx][actual_amp_idx]
                
                for state_idx_idx, state_idx in enumerate(self.state_indices):
                    displaced_state_vec = self.displaced_state(omega_d, amp, state_idx, coefficients[state_idx_idx])
                    floquet_mode = floquet_modes[omega_d_idx, amp_idx, state_idx_idx]
                    
                    overlap = np.vdot(displaced_state_vec, floquet_mode)
                    overlaps[omega_d_idx, amp_idx, state_idx_idx] = overlap
        
        return np.abs(overlaps)