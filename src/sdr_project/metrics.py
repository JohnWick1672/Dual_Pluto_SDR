import numpy as np

def calculate_ber(transmitted_bits, received_bits):
    """
    Calculate bit error rate.

    Parameters:
        transmitted_bits: Original transmitted binary sequence.
        received_bits: Recovered binary sequence.

    Returns:
        BER as a floating-point value.
    """
    # making sure input is in numpy array format
    transmitted_bits = np.asanyarray(transmitted_bits)
    received_bits = np.asanyarray(received_bits)


    # verify matching length and no empty sequences
    if len(transmitted_bits) != len(received_bits):
        raise ValueError('bit sequences must have the same length!')
    if len(transmitted_bits) == 0 or len(received_bits) == 0:
        raise ValueError('Bit sequences cannot be empty.')

    # making sure input arrays are actually bits
    if not np.all(np.isin(transmitted_bits, [0, 1])):
        raise ValueError('Transmitted sequence must contain only binary values.')

    if not np.all(np.isin(received_bits, [0, 1])):
        raise ValueError('Received sequence must contain only binary values.')



    #BER calculation
    N_errors = np.sum(transmitted_bits != received_bits)
    N_bits = len(transmitted_bits)

    ber = N_errors/N_bits

    return ber
