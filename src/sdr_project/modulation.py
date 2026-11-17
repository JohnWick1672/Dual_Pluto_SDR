import numpy as np
from scipy.signal import resample_poly

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

def root_raised_cosine(beta,samples_per_symbol,span):
    """"
    Generate root-raised-cosine filter coefficients

    Parameters:
        beta(float): RRC rolloff factor
        samples_per_symbol(int): Number of samples per symbol
        span(int): Filter duration in symbols

    Returns: 
        np.ndarray: Normalized RRC filter coefficients
    """
    # Validate inputs
    if not (0 < beta <= 1):
        raise ValueError("Beta must be between 0 and 1.")

    if not isinstance(samples_per_symbol, (int, np.integer)) or samples_per_symbol <= 0:
        raise ValueError("Samples per symbol must be a positive integer.")

    if not isinstance(span, (int, np.integer)) or span <= 0:
        raise ValueError("Span must be a positive integer.")

    # Number of coefficients
    N = span * samples_per_symbol + 1

    # Working in symbol periods rather than seconds
    tau = np.linspace(-span / 2, span / 2, N)

    # Initialize coefficient array
    h_tau = np.zeros(N)

    # Evaluate general and special cases
    for i, t in enumerate(tau):

        # Special case: tau = 0
        if np.isclose(t, 0):
            h_tau[i] = 1 - beta + (4 * beta) / np.pi

        # Special case: tau = +/- 1/(4*beta)
        elif np.isclose(abs(t), 1 / (4 * beta)):
            h_tau[i] = (beta / np.sqrt(2)) * (
                (1 + 2 / np.pi) * np.sin(np.pi / (4 * beta))
                + (1 - 2 / np.pi) * np.cos(np.pi / (4 * beta))
            )

        # General case
        else:
            numerator = (
                np.sin(np.pi * (1 - beta) * t)
                + 4 * beta * t * np.cos(np.pi * (1 + beta) * t)
            )

            denominator = (
                np.pi * t * (1 - (4 * beta * t) ** 2)
            )

            h_tau[i] = numerator / denominator

    # Normalize filter coefficients to unit energy
    h_tau = h_tau / np.sqrt(np.sum(np.abs(h_tau) ** 2))

    return h_tau

def upsample_symbols(bpsk_symbols,samples_per_symbol):
    """
    Upsample BPSK symbols by inserting zeros between symbols

    Parameters:
        bpsk_symbols(array): Complex BPSK symbols
        samples_per_symbols: Number of samples per symbol
    Returns:
        np.ndarray: Upsampled symbol sequence
    
    """
    #Assertions for function
    if bpsk_symbols is None or len(bpsk_symbols) == 0:
        raise ValueError('Nonzero sequence of symbols or samples per symbol required')
    if not isinstance(samples_per_symbol, (int, np.integer)) or samples_per_symbol <= 0:
        raise ValueError('samples per symbol must be positive integer')

    #Initialize with correct length then fill in with corresponding symbol at every sample period
    padded_symbols = np.zeros(len(bpsk_symbols)* samples_per_symbol, dtype = complex)
    padded_symbols[::samples_per_symbol] = bpsk_symbols

    return padded_symbols
    
def pulse_shape(upsampled_symbols,rrc_coefficients):
    """
    Form a digital pulse waveform through convolution

    Parameters:
        upsampled_symbols (array): Complex upsampled symbols
        rrc_coefficients (array): RRC filter coefficients
    Returns:
        np.ndarray: Pulse shaped waveform

    """

    if upsampled_symbols is None or len(upsampled_symbols) == 0:
        raise ValueError("Upsampled symbols cannot be empty")

    if rrc_coefficients is None or len(rrc_coefficients) == 0:
        raise ValueError("RRC coefficients cannot be empty")

    convolution = np.convolve(
        upsampled_symbols,
        rrc_coefficients,
        mode='full'
    )

    return convolution

def resample_transmit_signal(waveform,interpolation_factor):
    """
    Resample the 40 KSPS signal up to 1 MSPS for RF transmission

    Parameters:
        waveform(array): Pulsed waveform
        interpolation_factor(int): Integer interpolation factor
    
    Returns:
        np.ndarray: Resampled complex IQ waveform

    """
    #validate input
    if waveform is None or len(waveform) == 0:
        raise ValueError('Input waveform cannot be empty')
    if not isinstance(interpolation_factor, (int, np.integer)) or interpolation_factor <= 0:
        raise ValueError('Interpolation factor must be a positive integer')

    #performing the interpolation and low pass filtering
    tx_samples = resample_poly(waveform, up = interpolation_factor, down =1)

    return tx_samples   

