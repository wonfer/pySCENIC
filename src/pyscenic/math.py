# coding=utf-8


import numpy as np
from numba import *


@njit(signature_or_function=float64(float64[:], float64[:], float64))
def masked_rho(x: np.ndarray, y: np.ndarray, mask: float = 0.0) -> float:
    """
    Calculates the masked correlation coefficient of two vectors.

    :param x: A vector with the observations of a single variable.
    :param y: Another vector with the same number of observations for a variable.
    :param mask: The value to be masked.
    :return: Pearson correlation coefficient for x and y.
    """
    idx = (x != mask) & (y != mask)
    x_masked = x[idx]
    y_masked = y[idx]
    if (len(x_masked) == 0) or (len(y_masked) == 0):
        return np.nan
    x_demeaned = x_masked - x_masked.mean()
    y_demeaned = y_masked - y_masked.mean()
    cov_xy = np.dot(x_demeaned, y_demeaned)
    std_x = np.sqrt(np.dot(x_demeaned, x_demeaned))
    std_y = np.sqrt(np.dot(y_demeaned, y_demeaned))
    if (std_x * std_y) == 0:
        return np.nan
    return cov_xy / (std_x * std_y)


@njit(signature_or_function=float64[:, :](float64[:, :], float64[:, :], float64), parallel=True)
def masked_rho_2d(x: np.ndarray, y: np.ndarray, mask: float = 0.0) -> np.ndarray:
    """
    Calculates the masked correlation coefficients of two arrays.

    :param x: array of n variables and m observations (nxm).
    :param y: array of p variables and m observations (pxm).
    :param mask: the value to be masked.
    :return: array with correlation coefficients (nxp).
    """
    #Numba can parallelize loops automatically but this is still an experimental feature.
    n = x.shape[0]
    p = y.shape[0]
    rhos = np.empty(shape=(n, p), dtype=np.float64)
    for n_idx in prange(n):
        for p_idx in range(p):
            rhos[n_idx, p_idx] = masked_rho(x[n_idx, :], y[p_idx, :], mask)
    return rhos
