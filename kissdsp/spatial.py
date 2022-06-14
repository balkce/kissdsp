import numpy as np


def scm(Xs, Ms=None):
    """
    Compute the Spatial Correlation Matrix

    Args:
        Xs (np.ndarray):
            The time-frequency representation (nb_of_channels, nb_of_frames, nb_of_bins)
        Ms (np.ndarray):
            The time-frequency mask (nb_of_channels, nb_of_frames, nb_of_bins). If set to None, then mask is all 1's.

    Returns:
        (np.ndarray):
            The spatial correlation matrix (nb_of_bins, nb_of_channels, nb_of_channels)
    """

    nb_of_channels = Xs.shape[0]
    nb_of_frames = Xs.shape[1]
    nb_of_bins = Xs.shape[2]

    if Ms is None:
        Ms = np.ones(Xs.shape, dtype=np.float32)

    XXs = np.zeros((nb_of_bins, nb_of_channels, nb_of_channels), dtype=np.csingle)

    for bin_index in range(0, nb_of_bins):

        X = Xs[:, :, bin_index]
        M = Ms[:, :, bin_index]

        XM = X * M
        XXs[bin_index, :, :] = XM @ XM.conj().T

    return XXs


def steering(XXs):
    """
    Compute the Steering Vector (rank 1)

    Args:
        XXs (np.ndarray):
            The spatial correlation matrix (nb_of_bins, nb_of_channels, nb_of_channels)

    Returns:
        (np.ndarray):
            The steering vector in the frequency domain (nb_of_bins, nb_of_channels)
    """

    nb_of_bins = XXs.shape[0]
    nb_of_channels = XXs.shape[1]

    vs = np.linalg.eigh(XXs)[1][:, :, -1]
    v0s = np.tile(np.expand_dims(vs[:, 0], axis=1), (1, nb_of_channels))
    vs /= np.exp(1j * np.angle(v0s))

    return vs


def freefield(tdoas, frame_size=512):
    """
    Generate the Free Field Spatial Correlation Matrix (rank 1)

    Args:
        tdoas (np.ndarray):
            The time differences of arrival for each channel (nb_of_channels).
    frame_size (int):
        Number of samples per window.

    Returns:
        (np.ndarray):
            The spatial correlation matrix (nb_of_bins, nb_of_channels, nb_of_channels).
    """

    nb_of_channels = len(tdoas)
    nb_of_bins = int(frame_size/2)+1

    ks = np.arange(0, nb_of_bins)
    As = np.exp(-1j * 2.0 * np.pi * np.expand_dims(ks, axis=1) @ np.expand_dims(tdoas, axis=0) / frame_size)
    AAs = np.expand_dims(As, axis=2) @ np.conj(np.expand_dims(As, axis=1))

    return AAs


def rotmat(yaw, pitch, roll):
    """
    Generate a rotation matrix with given yaw, pitch and roll

    Args:
        yaw (float):
            Yaw angle (in rad).
        pitch (float):
            Pitch angle (in rad).
        roll (float):
            Roll angle (in rad).

    Returns:
        (np.ndarray):
            The rotation matrix (3, 3).

    """

    R = np.zeros((3,3), dtype=np.float32)

    alpha = yaw
    beta = pitch
    gamma = roll    

    R[0, 0] = np.cos(beta) * np.cos(gamma)
    R[0, 1] = np.sin(alpha) * np.sin(beta) * np.cos(gamma) - np.cos(alpha) * np.sin(gamma)
    R[0, 2] = np.cos(alpha) * np.sin(beta) * np.cos(gamma) + np.sin(alpha) * np.sin(gamma)
    R[1, 0] = np.cos(beta) * np.sin(gamma)
    R[1, 1] = np.sin(alpha) * np.sin(beta) * np.sin(gamma) + np.cos(alpha) * np.cos(gamma)
    R[1, 2] = np.cos(alpha) * np.sin(beta) * np.sin(gamma) - np.sin(alpha) * np.cos(gamma)
    R[2, 0] = -np.sin(beta)
    R[2, 1] = np.sin(alpha) * np.cos(beta)
    R[2, 2] = np.cos(alpha) * np.cos(beta)

    return R

