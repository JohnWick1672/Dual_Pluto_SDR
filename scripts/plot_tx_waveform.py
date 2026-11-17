import sys
sys.path.insert(0, "src")

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

from sdr_project.modulation import (
    bpsk_modulation,
    upsample_symbols,
    root_raised_cosine,
    pulse_shape,
    resample_transmit_signal
)

# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

bit_rate = 10_000
samples_per_symbol = 4
original_fs = bit_rate * samples_per_symbol

interpolation_factor = 25
tx_fs = original_fs * interpolation_factor

beta = 0.35
span = 10

# Reproducible random test data
rng = np.random.default_rng(42)
bits = rng.integers(0, 2, 10_000)

# --------------------------------------------------
# 2. BPSK modulation
# --------------------------------------------------

symbols = bpsk_modulation(bits)

# --------------------------------------------------
# 3. Upsampling
# --------------------------------------------------

upsampled = upsample_symbols(
    symbols,
    samples_per_symbol
)

# --------------------------------------------------
# 4. RRC filter generation
# --------------------------------------------------

rrc = root_raised_cosine(
    beta=beta,
    samples_per_symbol=samples_per_symbol,
    span=span
)

# --------------------------------------------------
# 5. Pulse shaping
# --------------------------------------------------

waveform = pulse_shape(upsampled, rrc)

# --------------------------------------------------
# 6. Sample-rate conversion
# --------------------------------------------------

tx_samples = resample_transmit_signal(
    waveform,
    interpolation_factor
)

# --------------------------------------------------
# 7. Print signal information
# --------------------------------------------------

print("\nTRANSMITTER VALIDATION")
print("----------------------")

print("Number of bits:", len(bits))
print("Number of symbols:", len(symbols))
print("Original waveform samples:", len(waveform))
print("Resampled waveform samples:", len(tx_samples))

print("Original sample rate:", original_fs, "S/s")
print("Final sample rate:", tx_fs, "S/s")

print("Complex output:", np.iscomplexobj(tx_samples))
print("Finite values:", np.all(np.isfinite(tx_samples)))

# --------------------------------------------------
# 8. Validate output
# --------------------------------------------------

assert len(tx_samples) == len(waveform) * interpolation_factor
assert np.iscomplexobj(tx_samples)
assert np.all(np.isfinite(tx_samples))

print("\nPASS: Transmitter waveform generation validated.")

# --------------------------------------------------
# 9. Calculate power spectral density
# --------------------------------------------------

f_before, psd_before = welch(
    waveform,
    fs=original_fs,
    nperseg=8192,
    return_onesided=False
)

f_after, psd_after = welch(
    tx_samples,
    fs=tx_fs,
    nperseg=16384,
    return_onesided=False
)

# Shift zero frequency to the center
f_before = np.fft.fftshift(f_before)
psd_before = np.fft.fftshift(psd_before)

f_after = np.fft.fftshift(f_after)
psd_after = np.fft.fftshift(psd_after)

# Normalize PSD relative to its maximum
psd_before_db = 10 * np.log10(
    np.maximum(psd_before / np.max(psd_before), 1e-12)
)

psd_after_db = 10 * np.log10(
    np.maximum(psd_after / np.max(psd_after), 1e-12)
)

# --------------------------------------------------
# 10. Estimate 99% occupied bandwidth
# --------------------------------------------------

df = f_after[1] - f_after[0]

cumulative_power = np.cumsum(psd_after) * df
total_power = cumulative_power[-1]

lower_index = np.searchsorted(cumulative_power, 0.005 * total_power)
upper_index = np.searchsorted(cumulative_power, 0.995 * total_power)

lower_freq = f_after[lower_index]
upper_freq = f_after[upper_index]

occupied_bandwidth = upper_freq - lower_freq

print("\nSPECTRAL ANALYSIS")
print("-----------------")
print("99% occupied bandwidth:", occupied_bandwidth / 1000, "kHz")
print("Theoretical RRC bandwidth:", (1 + beta) * bit_rate / 1000, "kHz")

# --------------------------------------------------
# 11. Time-domain waveform
# --------------------------------------------------

time = np.arange(len(tx_samples)) / tx_fs

plt.figure(figsize=(11, 5))

# Show a short section of the waveform
plt.plot(time[:1000] * 1000, np.real(tx_samples[:1000]))

plt.title("Interpolated BPSK Transmit Waveform")
plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.tight_layout()

# --------------------------------------------------
# 12. Compare spectra before and after interpolation
# --------------------------------------------------

plt.figure(figsize=(11, 5))

plt.plot(
    f_before / 1000,
    psd_before_db,
    label="Before interpolation (40 kS/s)"
)

plt.plot(
    f_after / 1000,
    psd_after_db,
    label="After interpolation (1 MSPS)"
)

plt.title("Transmit Spectrum Before and After Interpolation")
plt.xlabel("Frequency (kHz)")
plt.ylabel("Normalized PSD (dB)")
plt.xlim(-100, 100)
plt.ylim(-100, 5)
plt.legend()
plt.grid(True)
plt.tight_layout()

# --------------------------------------------------
# 13. Inspect the main signal bandwidth
# --------------------------------------------------

plt.figure(figsize=(11, 5))

plt.plot(f_after / 1000, psd_after_db)

plt.axvline(-6.75, linestyle="--", label="Ideal RRC band edges")
plt.axvline(6.75, linestyle="--")

plt.title("Interpolated BPSK Baseband Spectrum")
plt.xlabel("Frequency (kHz)")
plt.ylabel("Normalized PSD (dB)")
plt.xlim(-30, 30)
plt.ylim(-100, 5)
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()
