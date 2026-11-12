import numpy as np

def bpsk_modulation(bits):
    """
    Input: Sequence of binary bits (0s and 1s).
    Output: NumPy array of complex-valued BPSK symbols.
    """
    # convert into numpy array
    bits = np.asanyarray(bits)

    #check input and verify its in bit format
    if bits.size == 0:
        raise ValueError('Input bit sequence cant be empty')

    if not np.all(np.isin(bits,[0,1])):
        raise ValueError('Input must contain only binary values (0 and 1).')
    
    # assign each bit a mapping on real axis
    s_k = np.where(bits == 0, 1, -1)
    symbols = s_k.astype(complex)
    return symbols




