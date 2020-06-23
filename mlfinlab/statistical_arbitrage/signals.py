# pylint: disable=bare-except
"""
Implements Signals.
"""

import numpy as np
import pandas as pd
import warnings


def z_score(data):
    """
    Calculates the z-score for the given data.

    :param data: (np.array) Data for z-score calculation.
    :return: (np.array) Z-score of the given data.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = np.nan_to_num((data - np.mean(data, axis=0)) / np.std(data, axis=0))
    return res


def s_score(data):
    """
    Calculates the s-score, calculated with the ornstein-uhlenbeck process, for the given data.

    :param data: (np.array) Data for s-score calculation.
    :return: (np.array) S-score of the given data.
    """
    res = np.zeros(data.shape)
    for i in range(data.shape[1]):
        res[:, [i]] = _s_score(data[:, i])
    return res


def _s_score(_data):
    """
    Helper function to loop each column for s_score.

    :param _data: (np.array) Data for s-score calculation.
    :return: (np.array) S-score of the given data.
    """
    _data = _data.reshape((_data.size, 1))
    # Shift x down 1.
    data_x = _data[:-1]

    # Add constant.
    data_x = _add_constant(data_x.reshape((data_x.size, 1)))

    # Shift y up 1.
    data_y = _data[1:]

    # Calculate beta.
    beta = _linear_regression(data_x, data_y)

    # Calculate residuals.
    resid = data_y - data_x.dot(beta)

    # Set variables.
    a = beta[-1]
    b = beta[0]
    zeta = np.var(resid, axis=0)
    kappa = -np.log(b) * 252
    m = a / (1 - b)
    var_eq = np.sqrt(zeta / (1 - b ** 2))

    # Set signal.
    signal = (_data - m) / var_eq
    return signal


def hurst(data):
    return


def _linear_regression(data_x, data_y):
    """
    Calculates the parameter vector using matrix multiplication.

    :param data_x: (np.array) Time series of log returns of x.
    :param data_y: (np.array) Time series of log returns of y.
    :return: (np.array) Parameter vector.
    """
    try:
        beta = np.linalg.inv(data_x.T.dot(data_x)).dot(data_x.T).dot(data_y)
    except:
        beta = np.linalg.pinv(data_x.T.dot(data_x)).dot(data_x.T).dot(data_y)
    return beta


def _add_constant(returns):
    """
    Adds a constant of 1 on the right side of the given returns.

    :param returns: (np.array) Log returns for a given time series.
    :return: (np.array) Log returns with an appended column of 1 on the right.
    """
    #  Adds a column of 1 on the right side of the given array.
    return np.hstack((returns, np.ones((returns.shape[0], 1))))