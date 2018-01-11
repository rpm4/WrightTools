"""Array interaction tools."""


# --- import --------------------------------------------------------------------------------------


import numpy as np

from .. import exceptions as wt_exceptions


# --- define --------------------------------------------------------------------------------------


__all__ = ['closest_pair', 'diff', 'fft', 'joint_shape', 'remove_nans_1D', 'share_nans',
           'smooth_1D', 'unique']


# --- functions -----------------------------------------------------------------------------------


def closest_pair(arr, give='indicies'):
    """Find the pair of indices corresponding to the closest elements in an array.

    If multiple pairs are equally close, both pairs of indicies are returned.
    Optionally returns the closest distance itself.

    I am sure that this could be written as a cheaper operation. I
    wrote this as a quick and dirty method because I need it now to use on some
    relatively small arrays. Feel free to refactor if you need this operation
    done as fast as possible. - Blaise 2016-02-07

    Parameters
    ----------
    arr : numpy.ndarray
        The array to search.
    give : {'indicies', 'distance'} (optional)
        Toggle return behavior. If 'distance', returns a single float - the
        closest distance itself. Default is indicies.

    Returns
    -------
    list of lists of two tuples
        List containing lists of two tuples: indicies the nearest pair in the
        array.

        >>> arr = np.array([0, 1, 2, 3, 3, 4, 5, 6, 1])
        >>> closest_pair(arr)
        [[(1,), (8,)], [(3,), (4,)]]

    """
    idxs = [idx for idx in np.ndindex(arr.shape)]
    outs = []
    min_dist = arr.max() - arr.min()
    for idxa in idxs:
        for idxb in idxs:
            if idxa == idxb:
                continue
            dist = abs(arr[idxa] - arr[idxb])
            if dist == min_dist:
                if not [idxb, idxa] in outs:
                    outs.append([idxa, idxb])
            elif dist < min_dist:
                min_dist = dist
                outs = [[idxa, idxb]]
    if give == 'indicies':
        return outs
    elif give == 'distance':
        return min_dist
    else:
        raise KeyError('give not recognized in closest_pair')


def diff(xi, yi, order=1):
    """Take the numerical derivative of a 1D array.

    Output is mapped onto the original coordinates  using linear interpolation.

    Parameters
    ----------
    xi : 1D array-like
        Coordinates.
    yi : 1D array-like
        Values.
    order : positive integer (optional)
        Order of differentiation.

    Returns
    -------
    1D numpy array
        Numerical derivative. Has the same shape as the input arrays.
    """
    xi = np.array(xi).copy()
    yi = np.array(yi).copy()
    arg = np.argsort(xi)
    xi = xi[arg]
    yi = yi[arg]
    midpoints = (xi[1:] + xi[:-1]) / 2
    for _ in range(order):
        d = np.diff(yi)
        d /= np.diff(xi)
        yi = np.interp(xi, midpoints, d)
    return yi[arg]


def fft(xi, yi, axis=0):
    """Take the 1D FFT of an N-dimensional array and return "sensible" properly shifted arrays.

    Parameters
    ----------
    xi : numpy.ndarray
        1D array over which the points to be FFT'ed are defined
    yi : numpy.ndarray
        ND array with values to FFT
    axis : int
        axis of yi to perform FFT over

    Returns
    -------
    xi : 1D numpy.ndarray
        1D array. Conjugate to input xi. Example: if input xi is in the time
        domain, output xi is in frequency domain.
    yi : ND numpy.ndarray
        FFT. Has the same shape as the input array (yi).
    """
    # xi must be 1D
    if xi.ndim != 1:
        raise wt_exceptions.DimensionalityError(1, xi.ndim)
    # xi must be evenly spaced
    spacing = np.diff(xi)
    if not np.allclose(spacing, spacing.mean()):
        raise RuntimeError('WrightTools.kit.fft: argument xi must be evenly spaced')
    # fft
    yi = np.fft.fft(yi, axis=axis)
    d = (xi.max() - xi.min()) / (xi.size - 1)
    xi = np.fft.fftfreq(xi.size, d=d)
    # shift
    xi = np.fft.fftshift(xi)
    yi = np.fft.fftshift(yi, axes=axis)
    return xi, yi


def joint_shape(arrs):
    """Given a list of arrays, return the joint shape.

    Parameters
    ----------
    arrs : list of array-like
        Input arrays.

    Returns
    -------
    tuple of int
        Joint shape.
    """
    if len(arrs) == 0:
        return ()
    shape = []
    shapes = [a.shape for a in arrs]
    ndim = arrs[0].ndim
    for i in range(ndim):
        shape.append(max([s[i] for s in shapes]))
    return tuple(shape)


def remove_nans_1D(arrs):
    """Remove nans in a list of 1D arrays.

    Removes indicies in all arrays if any array is nan at that index.
    All input arrays must have the same size.

    Parameters
    ----------
    arrs : list of 1D arrays
        The arrays to remove nans from

    Returns
    -------
    list
        List of 1D arrays in same order as given, with nan indicies removed.
    """
    # find all indicies to keep
    bads = np.array([])
    for arr in arrs:
        bad = np.array(np.where(np.isnan(arr))).flatten()
        bads = np.hstack((bad, bads))
    if hasattr(arrs, 'shape') and len(arrs.shape) == 1:
        goods = [i for i in np.arange(arrs.shape[0]) if i not in bads]
    else:
        goods = [i for i in np.arange(len(arrs[0])) if i not in bads]
    # apply
    return [a[goods] for a in arrs]


def share_nans(arrs):
    """Take a list of nD arrays and return a new list of nD arrays.

    The new list is in the same order as the old list.
    If one indexed element in an old array is nan then every element for that
    index in all new arrays in the list is then nan.

    Parameters
    ----------
    arrs : list of nD arrays
        The arrays to syncronize nans from

    Returns
    -------
    list
        List of nD arrays in same order as given, with nan indicies syncronized.
    """
    nans = np.zeros((arrs[0].shape))
    for arr in arrs:
        nans *= arr
    return [a + nans for a in arrs]


def smooth_1D(arr, n=10):
    """Smooth 1D data by 'running average'.

    Parameters
    ----------
    n : int
        number of points to average
    """
    for i in range(n, len(arr) - n):
        window = arr[i - n:i + n].copy()
        arr[i] = window.mean()
    return arr


def unique(arr, tolerance=1e-6):
    """Return unique elements in 1D array, within tolerance.

    Parameters
    ----------
    arr : array_like
        Input array. This will be flattened if it is not already 1D.
    tolerance : number (optional)
        The tolerance for uniqueness.

    Returns
    -------
    array
        The sorted unique values.
    """
    arr = sorted(arr.flatten())
    unique = []
    while len(arr) > 0:
        current = arr[0]
        lis = [xi for xi in arr if np.abs(current - xi) < tolerance]
        arr = [xi for xi in arr if not np.abs(lis[0] - xi) < tolerance]
        xi_lis_average = sum(lis) / len(lis)
        unique.append(xi_lis_average)
    return np.array(unique)