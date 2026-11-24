import numpy as np
from scipy.signal import resample_poly
import numbers

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

def matched_rrc_filter(received_signal, rrc_coefficients):
    """
    A matched root raised cosine filter on the RX end to implement the full RRC response

    Parameters:
        received_signal(array): Complex IQ signal
        rrc_coefficients(array): The time reversed complex conjugate of the transmit filter coefficients

    Returns:
    The corresponding 

    """

    #Verifying the inputs
    if received_signal is None:
        raise ValueError("Input signal can't be NONE")
    if not isinstance(received_signal,np.ndarray):
        raise TypeError('Received signal must be a numpy array')
    if received_signal.size == 0:
        raise ValueError('Recieved signal must be nonempty')
    if not isinstance(rrc_coefficients, np.ndarray):
        raise TypeError('RRC coefficients must be an numpy array')
    if rrc_coefficients.size == 0:
        raise ValueError('RRC coefficients cant be empty')
    if not np.all(np.isfinite(received_signal)) or not np.all(np.isfinite(rrc_coefficients)):
        raise ValueError('Both inputs must be finite')
    if not np.iscomplexobj(received_signal):
        raise TypeError("Received signal must contain complex IQ samples")


    filtered_signal = np.convolve(received_signal, rrc_coefficients, mode = 'full')

    return filtered_signal


def interpolate_sample(received_signal, sample_position):
    """
    Performs interpolation to estimate the value of the received signal at the sampled position index

    Parameters:
        received_signal(numpy array): The complex IQ signal after rrc filtering
        sample_position(float): The index at which we want to estimate the value of the received signal

    Returns:
        Estimated value of received signal at sample position
    """
    #Validation checks
    if not isinstance(received_signal,np.ndarray):
        raise TypeError('Received signal must a numpy array')
    if received_signal.size == 0:
        raise ValueError('Empty received signal cannot be processed')
    if sample_position is None:
        raise ValueError('Sample position cant be NONE')
    if not isinstance(sample_position, (int, float, np.integer, np.floating)):
        raise TypeError("Sample position must be numeric")
    if sample_position < 0:
        raise ValueError('Sample position cant be negative')
    if sample_position >= len(received_signal) -1:
        raise ValueError('Sample position is exceeding the length of the received signal')
    if not np.isfinite(sample_position):
        raise ValueError("Sample position must be finite")
    
    #formula x(n + u) = (1- u)x[n] + ux[n+1]

    n = int(np.floor(sample_position))

    u = sample_position - n

    interpolated_sample = (1-u)*received_signal[n] + u*received_signal[n+1]

    return interpolated_sample

def gardner_timing_error(early_sample, middle_sample, late_sample):
    """
    Calculates the Gardner timing error using three samples.

    Parameters:
        early_sample: Sample taken half a symbol before the estimated center.
        middle_sample: Sample taken at the estimated symbol center.
        late_sample: Sample taken half a symbol after the estimated center.

    Returns:
        Estimated timing error
    """

    if not all(isinstance(x, numbers.Number) for x in (early_sample, middle_sample, late_sample)):
        raise TypeError("Samples must be numeric")
    if not np.isfinite(early_sample):
        raise ValueError('Early sample must be finite')
    if not np.isfinite(middle_sample):
            raise ValueError('Middle sample must be finite')
    if not np.isfinite(late_sample):
            raise ValueError('Late sample must be finite')

    error = np.real((early_sample-late_sample)* np.conjugate(middle_sample))

    return error

def timing_loop_filter(timing_error, prev_integral_state,kp,ki):
    """
    Applies a proportional-integral timing loop fiter.

    Parameters:
        timing_error: Gardner timing error
        integral_state: Previous accumulated integral value
        kp: Proportional gain
        ki: Integral gain

    Returns:
        timing_correction: Combined PI output
        updated_integral: Updated integral state
    """
    if not all(isinstance(x, numbers.Number) for x in (timing_error, prev_integral_state, kp,ki)):
            raise TypeError("Inputs must be numeric")
    if not np.isfinite(timing_error):
        raise ValueError('Gardner timing error must be finite')
    if not np.isfinite(prev_integral_state):
        raise ValueError('PreviousIntegral state must be finite')
    if not np.isfinite(kp):
        raise ValueError('Kp must be finite')
    if not np.isfinite(ki):
        raise ValueError('Ki must be finite')
    if kp < 0 or ki < 0:
        raise ValueError("PI gains must be nonnegative")

    #Update integral state
    updated_integral = prev_integral_state + ki*timing_error

    # timing correction to apply
    timing_correction = kp*timing_error + updated_integral

    return timing_correction, updated_integral


def timing_recovery(received_signal, samples_per_symbol, kp,ki):
    """
    Performs Gardner timing recovery using a PI feedback loop

    Parameters:
        received_signal: Complex valued IQ waveform after matched filtering
        samples_per_symbol: Nominal samples per symbol 
        kp: Proportional loop gain
        ki: Integral loop gain
    
    Returns:
        recovered_symbols: Timing-aligned complex symbol samples

    """
    #Initialize timing recovery variables
    sampling_position = 40
    integral_state = 0.0
    recovered_symbols = []
    half_symbol = (samples_per_symbol)/2

    #test stuff
    timing_errors = []
    timing_corrections = []
    sampling_positions = []

    while sampling_position + half_symbol < len(received_signal) -1:

        #Retreive the samples by interpolating
        received_early = interpolate_sample(received_signal, sampling_position-half_symbol)
        received_middle = interpolate_sample(received_signal,sampling_position )
        received_late = interpolate_sample(received_signal, sampling_position + half_symbol)

        # Find Gardner timing error
        error = gardner_timing_error(received_early,received_middle,received_late)

        #Apply the loop filter to get correction
        timing_correction, updated_integral = timing_loop_filter(error,integral_state,kp,ki)

        #updating integral state, recovered symbols and sampling postion
        integral_state = updated_integral
        recovered_symbols.append(received_middle)
        #test stuff
        timing_errors.append(error)
        timing_corrections.append(timing_correction)
        sampling_positions.append(sampling_position)    



        sampling_position += samples_per_symbol - timing_correction

    print("Average timing error:", np.mean(timing_errors))
    print("Average correction:", np.mean(timing_corrections))
    print("Final sampling position:", sampling_position)


    return np.asanyarray(recovered_symbols)