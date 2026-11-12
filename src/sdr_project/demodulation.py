import numpy as np
from sdr_project.modulation import bpsk_modulation


def bpsk_demodulation(received_symbols):

    """
    Recover binary bits from received BPSK symbols.

    Parameters:
        received_symbols: Complex-valued received symbols.

    Returns:
        NumPy array of recovered binary bits.
    """

    # convert to numpy array
    received_symbols = np.asanyarray(received_symbols)

    # Assign bits to each symbol depending on where they lie on the real axis
    bits = np.where(np.real(received_symbols) >= 0, 0, 1)

    return bits

def estimate_frequency_offset(received_symbols, sample_rate):
    """
    Estimate frequency offset from received BPSK symbols.

    Parameters:
        received_symbols: Received complex BPSK symbols.
        sample_rate: Sampling frequency in Hz.

    Returns:
        Estimated frequency offset in Hz.
    """
    # removing the BPSK data
    rk_squared = received_symbols**2
    #calculating phase difference
    phase_diff = np.angle(np.sum(rk_squared[1:] *np.conj(rk_squared[:-1]))) 


    # calculating the estimated frequency offset
    f_offset = (phase_diff * sample_rate)/(4*np.pi)

    return f_offset


def correct_frequency_offset(received_symbols, estimated_offset, sample_rate):
    """
    Correct frequency offset using an estimated frequency difference.

    Parameters:
        received_symbols: Received complex samples.
        estimated_offset: Estimated frequency offset in Hz.
        sample_rate: Sampling frequency in Hz.

    Returns:
        Frequency-corrected complex samples.
    """
    #k is number of symbols we have to account for 
    k = np.arange(len(received_symbols))

    #phase correction for each symbol
    phase_to_correct = (-1j *(2*np.pi)*estimated_offset*k)/(sample_rate)

    correct_symbols = received_symbols*np.exp(phase_to_correct)

    return correct_symbols


def bpsk_receiver_sync(received_symbols, sample_rate, preamble_bits=None,
                       alpha=0.05, beta=0.001):
    """
    BPSK carrier synchronization:
    1. Coarse frequency estimation and correction.
    2. Fine carrier recovery using a Costas loop.
    3. Optional 180-degree ambiguity correction using a known preamble.

    Assumes symbol timing is already aligned and one sample per symbol.
    """

    received_symbols = np.asarray(received_symbols, dtype=complex)

    if received_symbols.size == 0:
        raise ValueError("Received symbols cannot be empty.")

    # 1. Coarse frequency estimation
    estimated_offset = estimate_frequency_offset(
        received_symbols, sample_rate
    )

    # 2. Coarse frequency correction
    frequency_corrected = correct_frequency_offset(
        received_symbols, estimated_offset, sample_rate
    )

    # 3. Fine carrier recovery using a BPSK Costas loop
    phase = 0.0
    frequency = 0.0

    corrected_symbols = np.zeros_like(frequency_corrected)

    for k in range(len(frequency_corrected)):

        corrected_symbols[k] = (
            frequency_corrected[k] * np.exp(-1j * phase)
        )

        I = np.real(corrected_symbols[k])
        Q = np.imag(corrected_symbols[k])

        phase_error = np.sign(I) * Q

        frequency += beta * phase_error
        phase += frequency + alpha * phase_error

    # 4. Resolve the 180-degree phase ambiguity using a known preamble
    if preamble_bits is not None:

        preamble_bits = np.asarray(preamble_bits)

        if len(preamble_bits) > len(corrected_symbols):
            raise ValueError("Preamble is longer than received sequence.")

        expected_symbols = bpsk_modulation(preamble_bits)

        detected_symbols = np.real(corrected_symbols[:len(preamble_bits)])

        normal_errors = np.sum(
            (detected_symbols < 0) != (preamble_bits == 1)
        )

        inverted_errors = np.sum(
            (detected_symbols >= 0) != (preamble_bits == 1)
        )

        if inverted_errors < normal_errors:
            corrected_symbols *= -1

    return corrected_symbols, estimated_offset
