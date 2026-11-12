import numpy as np

def phase_offset_channel(symbols, phase_offset):
    """
    Apply a constant phase offset to transmitted symbols.

    Parameters:
        symbols: Array of transmitted complex symbols.
        phase_offset: Phase offset in radians.

    Returns:
        Phase-shifted complex symbols.
    """
    shifted_symbols = symbols *np.exp(1j * phase_offset)
    return shifted_symbols


def awgn_channel(symbols, snr_db):
    """
    Add complex AWGN to transmitted symbols.

    Parameters:
        symbols: Array of transmitted complex symbols.
        snr_db: Desired signal-to-noise ratio in dB.

    Returns:
        Received symbols corrupted by AWGN.
    """
    #transfering into numpy
    symbols = np.asanyarray(symbols, dtype= complex)

    #calculating average signal power
    Ps = np.mean(np.abs(symbols)**2)
    noise_deviation = np.sqrt(Ps/(2*(10**(snr_db/10))))

    #next we generate random I and Q noise
    noise_i = np.random.normal(0,noise_deviation, len(symbols))
    noise_q = np.random.normal(0,noise_deviation, len(symbols))

    #then we combine the noise into complex samples
    noise = noise_i + 1j * noise_q

    #add noise to transmitted symbols
    received_symbols = symbols + noise

    return received_symbols


def frequency_offset_channel(symbols, frequency_offset, sample_rate):
    """
    Apply a frequency offset to transmitted complex samples.

    Parameters:
        symbols: Array of transmitted complex samples.
        frequency_offset: Frequency offset in Hz.
        sample_rate: Sampling frequency in Hz.

    Returns:
        Frequency-shifted complex samples.
    """
    #the number of sample indices which is basically gonna apply some sort of offset to each symbol
    k = np.arange(len(symbols))
    phase = (2*np.pi * frequency_offset *k)/sample_rate
    f_shifted_symbols = symbols * np.exp(1j * phase)

    return f_shifted_symbols

