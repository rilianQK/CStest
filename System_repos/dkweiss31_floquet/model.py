import numpy as np
import itertools
import qutip as qt
from .utils.file_io import Serializable


class Model(Serializable):
    """Specify the model, including the Hamiltonian, drive strengths and frequencies.

    Can be subclassed to e.g. override the hamiltonian() method for a different (but
    still periodic!) Hamiltonian.

    Parameters:
        H0: Drift Hamiltonian, which must be diagonal and provided in units such that
            H0 can be passed directly to qutip.
        H1: Drive operator, which should be unitless (for instance the charge-number
            operator n of the transmon). It will be multiplied by a drive amplitude
            that we scan over from drive_parameters.drive_amplitudes.
        omega_d_values: drive frequencies to scan over
        drive_amplitudes: amp values to scan over. Can be one dimensional in which case
            these amplitudes are used for all omega_d, or it can be two dimensional
            in which case the first dimension are the amplitudes to scan over
            and the second are the amplitudes for respective drive frequencies
    """

    def __init__(self, H0, H1, omega_d_values, drive_amplitudes):
        """Initialize an object with Hamiltonian matrices (H0 and H1), drive frequency values (omega_d_values), and drive amplitudes (drive_amplitudes), ensuring proper type conversion and shape validation."""
        self.H0 = np.array(H0)
        self.H1 = np.array(H1)
        self.omega_d_values = np.array(omega_d_values)
        
        drive_amplitudes = np.array(drive_amplitudes)
        if drive_amplitudes.ndim == 1:
            self.drive_amplitudes = np.tile(drive_amplitudes, (len(omega_d_values), 1))
        else:
            self.drive_amplitudes = drive_amplitudes

    def hamiltonian(self, omega_d_amp):
        """Return the Hamiltonian we actually simulate."""
        omega_d, amp = omega_d_amp
        H0_qobj = qt.Qobj(self.H0)
        H1_qobj = qt.Qobj(self.H1)
        
        def H_coeff_t(t, args):
            return amp * np.cos(omega_d * t)
        
        return [H0_qobj, [H1_qobj, H_coeff_t]]

    def omega_d_to_idx(self, omega_d):
        """Return index corresponding to omega_d value."""
        return np.argmin(np.abs(self.omega_d_values - omega_d))

    def amp_to_idx(self, amp, omega_d):
        """Return index corresponding to amplitude value.

        Because the drive amplitude can depend on the drive frequency, we also must pass
        the drive frequency here.
        """
        omega_d_idx = self.omega_d_to_idx(omega_d)
        amplitudes_for_omega_d = self.drive_amplitudes[omega_d_idx]
        return np.argmin(np.abs(amplitudes_for_omega_d - amp))

    def omega_d_amp_params(self, amp_idxs):
        """Return ordered chain object of the specified omega_d and amplitude values."""
        params = []
        for omega_d_idx, omega_d in enumerate(self.omega_d_values):
            amplitudes = self.drive_amplitudes[omega_d_idx]
            start_idx, end_idx = amp_idxs
            for amp_idx in range(start_idx, end_idx):
                amp = amplitudes[amp_idx]
                params.append((omega_d, amp))
        return itertools.chain(params)