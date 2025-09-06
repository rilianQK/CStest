import numpy as np
from typing import Any, List, Optional, Tuple
from scipy.linalg import eigvalsh
from ..utils.file_io import Serializable


class ChiacToAmp(Serializable):
    """Convert given induced ac-stark shift values to drive amplitudes.

    Consider a qubit coupled to an oscillator with the interaction Hamiltonian
    $H_I = g(a + a^{\dagger})(b + b^{\dagger})$. If the oscillator is driven to
    an average occupation number of $\bar{n}$, then the effective drive strength
    seen by the qubit is $\Omega_d = 2 g \sqrt{\bar{n}}$. On the other hand based
    on a Schrieffer-Wolff transformation, the interaction hamiltonian is
    $H^{(2)} = \chi a^{\dagger}ab^{\dagger}b$. The average induced
    ac-stark shift is then $\chi_{ac} = \chi \bar{n}$. Thus $\Omega_d = 2g\sqrt{\chi_{\rm ac}/\chi}$.
    Observe that since $\chi \sim g^2$, $g$ effectively cancels out and can be set to 1.
    
    noqa E501
    """

    def __init__(self, H0, H1, state_indices, omega_d_values):
        """Initialize the object with Hamiltonian operators H0 and H1, a list of state indices, and an array of driving frequency values."""
        self.H0 = H0
        self.H1 = H1
        self.state_indices = state_indices
        self.omega_d_linspace = omega_d_values

    @staticmethod
    def chi_ell_ellp(energies, H1, E_osc, ell, ellp):
        """Calculate the transition matrix element between energy states ell and ellp for a given oscillator energy E_osc, using the provided Hamiltonian matrix H1 and energy levels."""
        if ell == ellp:
            return 0.0
        
        delta_ell_ellp = energies[ell] - energies[ellp]
        H1_ell_ellp = H1[ell, ellp]
        
        return H1_ell_ellp**2 * (1 / (delta_ell_ellp + E_osc) + 1 / (delta_ell_ellp - E_osc))

    def chi_ell(self, energies, H1, E_osc, ell):
        """Compute the difference between the sum of chi_ell_ellp values for all ellp and the sum of chi_ellp_ell values for all ellp, given energies, H1 matrix, E_osc, and ell."""
        chi_sum = 0.0
        for ellp in range(len(energies)):
            if ellp != ell:
                chi_sum += self.chi_ell_ellp(energies, H1, E_osc, ell, ellp)
        
        return chi_sum

    def compute_chis_for_omega_d(self):
        """Compute chi difference for the first two states in state_indices.

        Based on the analysis in Zhu et al PRB (2013)
        """
        energies = eigvalsh(self.H0)
        H1_matrix = self.H1
        
        chis = []
        for omega_d in self.omega_d_linspace:
            chi_0 = self.chi_ell(energies, H1_matrix, omega_d, self.state_indices[0])
            chi_1 = self.chi_ell(energies, H1_matrix, omega_d, self.state_indices[1])
            chis.append(chi_1 - chi_0)
        
        return np.array(chis)

    def amplitudes_for_omega_d(self, chi_ac_linspace):
        """Return drive amplitudes corresponding to $\chi_{\rm ac}$ values."""
        chis = self.compute_chis_for_omega_d()
        amplitudes = []
        
        for i, omega_d in enumerate(self.omega_d_linspace):
            chi = chis[i]
            if chi <= 0:
                amplitudes.append(np.zeros_like(chi_ac_linspace))
            else:
                amplitudes.append(2 * np.sqrt(chi_ac_linspace / chi))
        
        return np.array(amplitudes)


class XiSqToAmp(Serializable):
    """Convert given $|\xi|^2$ value into a drive amplitude.

    This is based on the equivalence $\xi = 2 \Omega_d \omega_d / (\omega_d^2-\omega^2)$,
    where in this definition $|\xi|^2= 2 \chi_{\rm ac} / \alpha$ where $\chi_{\rm ac}$ is
    the induced ac stark shift, $\alpha$ is the anharmonicity and $\Omega_d$ is the
    drive amplitude.
    
    noqa E501
    """

    def __init__(self, H0, H1, state_indices, omega_d_linspace):
        """Initialize an instance of the class with the given Hamiltonian operators (H0 and H1), state indices, and a linear space of driving frequencies (omega_d_linspace)."""
        self.H0 = H0
        self.H1 = H1
        self.state_indices = state_indices
        self.omega_d_linspace = omega_d_linspace

    def amplitudes_for_omega_d(self, xi_sq_linspace):
        """Return drive amplitudes corresponding to $|\xi|^2$ values."""
        energies = eigvalsh(self.H0)
        anharmonicity = energies[2] - 2 * energies[1] + energies[0]
        
        amplitudes = []
        for omega_d in self.omega_d_linspace:
            amp = np.sqrt(xi_sq_linspace * anharmonicity / 2)
            amplitudes.append(amp)
        
        return np.array(amplitudes)