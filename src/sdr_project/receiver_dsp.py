import numpy as np
from scipy.signal import resample_poly

def decimate_received_signal(received_signal, decimation_factor):
    """
    Decimate to reduce the sampling rate of recieved by decimation factor

    Parameters:
        recieved_signal(array): signal to be decimated
        decimation_factor(int)

    Returns:
    Returns the recieved signal decimated by decimation factor
    """
    #Quick validations on input
    if received_signal is None:
        raise ValueError('Received signal cant be NONE')
    if not isinstance(decimation_factor,int) or isinstance(decimation_factor,bool):
        raise TypeError('Decimation factor must be an integer')
    if decimation_factor <= 0:
        raise ValueError('Decimation factor be a positive integer')
    if not isinstance(received_signal,np.ndarray):
        raise TypeError('Received signal must be Numpy array')
    if received_signal.size == 0:
        raise ValueError('Received signal cant be empty')
    if not np.iscomplexobj(received_signal):
        raise TypeError('Received signal must contain complex IQ samples')

    # Decimation operation
    decimated_signal = resample_poly(received_signal, up = 1, down = decimation_factor)

    return decimated_signal