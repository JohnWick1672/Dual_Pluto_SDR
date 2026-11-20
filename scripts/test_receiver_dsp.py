import sys
sys.path.insert(0, "src")
import matplotlib.pyplot as plt

from scipy.signal import welch

import numpy as np
from sdr_project.receiver_dsp import decimate_received_signal
from sdr_project.modulation import bpsk_modulation,pulse_shape,root_raised_cosine,resample_transmit_signal,upsample_symbols


#Random bit sequence
rng = np.random.default_rng(42)
bits = rng.integers(0,2,size = 1000)

#Generate modulated signal
modulated_signal = bpsk_modulation(bits)

#Upsample to 4 samples per symbol
upsampled_signal = upsample_symbols(modulated_signal,4)

#Generate RRC coefficients
rrc_coe = root_raised_cosine(beta=0.35, samples_per_symbol=4,span = 10)

#Pulse Shape
pulsed_waveform = pulse_shape(upsampled_signal, rrc_coe)

#Interpolate to meet 1MSPS requirement of SDR
final_waveform = resample_transmit_signal(pulsed_waveform, 25)

#after reception, the decimation
decimated_waveform = decimate_received_signal(final_waveform, decimation_factor=25)


print("Original waveform: ", pulsed_waveform.shape)
print('Interpolated waveform: ', final_waveform.shape)
print('Decimated waveform: ', decimated_waveform.shape)

print("Complex output? ", np.iscomplexobj(decimated_waveform))
print('All finite? ', np.all(np.isfinite(decimated_waveform)))

#Error between waveforms check
error = pulsed_waveform - decimated_waveform

mse = np.mean(np.abs(error)**2)

print("Mean squared error:", mse)
signal_power = np.mean(np.abs(pulsed_waveform)**2)

nrmse = np.sqrt(mse / signal_power)

print("Original signal power:", signal_power)
print("Normalized RMSE:", nrmse)
print("Normalized RMSE (%):", nrmse * 100)


plt.figure(figsize=(12, 5))

plt.plot(np.real(pulsed_waveform[:200]), label="Original waveform")
plt.plot(np.real(decimated_waveform[:200]), "--", label="Decimated waveform")

plt.xlabel("Sample index")
plt.ylabel("Amplitude")
plt.title("Original vs. Decimated Waveform")
plt.legend()
plt.grid(True)
plt.show()



fs = 40_000  # Sampling rate after decimation

f_original, psd_original = welch(
    pulsed_waveform,
    fs=fs,
    nperseg=1024,
    return_onesided=False
)

f_decimated, psd_decimated = welch(
    decimated_waveform,
    fs=fs,
    nperseg=1024,
    return_onesided=False
)

plt.figure(figsize=(12, 5))

plt.plot(
    np.fft.fftshift(f_original),
    10 * np.log10(np.fft.fftshift(psd_original)),
    label="Original"
)

plt.plot(
    np.fft.fftshift(f_decimated),
    10 * np.log10(np.fft.fftshift(psd_decimated)),
    "--",
    label="Decimated"
)

plt.xlabel("Frequency (Hz)")
plt.ylabel("PSD (dB/Hz)")
plt.title("Original vs. Decimated Signal Spectrum")
plt.legend()
plt.grid(True)
plt.show()