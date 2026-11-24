
import sys
sys.path.insert(0, "src")

import numpy as np
from scipy.signal import resample_poly

from sdr_project.modulation import (
    bpsk_modulation,
    pulse_shape,
    root_raised_cosine,
    resample_transmit_signal,
    upsample_symbols
)

from sdr_project.receiver_dsp import (
    decimate_received_signal,
    matched_rrc_filter,
    interpolate_sample,
    gardner_timing_error,
    timing_loop_filter,
    timing_recovery
)


# ============================================================
# TEST SETUP: Generate common test signal
# ============================================================

rng = np.random.default_rng(42)

bits = rng.integers(0, 2, size=1000)
symbols = bpsk_modulation(bits)

samples_per_symbol = 4

rrc = root_raised_cosine(
    beta=0.35,
    samples_per_symbol=samples_per_symbol,
    span=10
)

upsampled = upsample_symbols(symbols, samples_per_symbol)
tx_waveform = pulse_shape(upsampled, rrc)

# Apply receiver matched filter
rx_filtered = matched_rrc_filter(
    tx_waveform.astype(complex),
    rrc
)

# Combined TX and RX group delay
group_delay = len(rrc) - 1


# ============================================================
# TEST 1: Interpolation and decimation
# ============================================================

print("\nTEST 1: Interpolation and decimation")

interpolated = resample_transmit_signal(
    tx_waveform,
    interpolation_factor=25
)

decimated = decimate_received_signal(
    interpolated,
    decimation_factor=25
)

assert len(decimated) == len(tx_waveform)
assert np.iscomplexobj(decimated)
assert np.all(np.isfinite(decimated))

mse = np.mean(np.abs(tx_waveform - decimated)**2)

nrmse = np.sqrt(
    mse / np.mean(np.abs(tx_waveform)**2)
)

print("Decimation test passed!")
print(f"Original length: {len(tx_waveform)}")
print(f"Interpolated length: {len(interpolated)}")
print(f"Decimated length: {len(decimated)}")
print(f"NRMSE: {nrmse:.6%}")


# ============================================================
# TEST 2: Matched RRC filtering and zero ISI
# ============================================================

print("\nTEST 2: Matched RRC filtering and zero ISI")

expected_length = len(tx_waveform) + len(rrc) - 1

assert len(rx_filtered) == expected_length
assert np.iscomplexobj(rx_filtered)
assert np.all(np.isfinite(rx_filtered))

symbol_indices = (
    group_delay
    + np.arange(len(symbols)) * samples_per_symbol
)

recovered_symbols = rx_filtered[symbol_indices]

error = recovered_symbols - symbols

mse = np.mean(np.abs(error)**2)

evm = np.sqrt(
    np.sum(np.abs(error)**2)
    / np.sum(np.abs(symbols)**2)
)

max_error = np.max(np.abs(error))

print("Matched RRC test passed!")
print(f"TX waveform length: {len(tx_waveform)}")
print(f"RX filtered length: {len(rx_filtered)}")
print(f"Total group delay: {group_delay} samples")
print(f"Recovered symbols: {len(recovered_symbols)}")
print(f"Symbol MSE: {mse:.8e}")
print(f"Symbol EVM: {evm:.6%}")
print(f"Maximum symbol error: {max_error:.8e}")

assert evm < 0.01, "Matched filter has unexpectedly high symbol error"


# ============================================================
# TEST 3: Linear interpolation
# ============================================================

print("\nTEST 3: Linear interpolation")

test_signal = np.array([
    1 + 2j,
    3 + 4j,
    5 + 6j,
    7 + 8j
])

result1 = interpolate_sample(test_signal, 1.0)
assert np.isclose(result1, 3 + 4j)

result2 = interpolate_sample(test_signal, 1.5)
expected2 = 0.5 * test_signal[1] + 0.5 * test_signal[2]
assert np.isclose(result2, expected2)

result3 = interpolate_sample(test_signal, 1.25)
expected3 = 0.75 * test_signal[1] + 0.25 * test_signal[2]
assert np.isclose(result3, expected3)

print("Interpolation tests passed!")
print(f"At index 1.0: {result1}")
print(f"At index 1.5: {result2}")
print(f"At index 1.25: {result3}")


# ============================================================
# TEST 4: Gardner timing error detector
# ============================================================

print("\nTEST 4: Gardner timing error detector")

# Real-valued samples
early = 0.5
middle = 1.0
late = -0.5

result1 = gardner_timing_error(
    early,
    middle,
    late
)

expected1 = (early - late) * middle

assert np.isclose(result1, expected1)

# Complex-valued samples
early = 1 + 2j
middle = 2 + 1j
late = -1 + 1j

result2 = gardner_timing_error(
    early,
    middle,
    late
)

expected2 = np.real(
    (early - late) * np.conjugate(middle)
)

assert np.isclose(result2, expected2)

print("Gardner tests passed!")
print(f"Real-valued timing error: {result1}")
print(f"Complex-valued timing error: {result2}")


# ============================================================
# TEST 5: PI timing loop filter
# ============================================================

print("\nTEST 5: PI timing loop filter")

timing_error = 0.2
prev_integral_state = 0.05

kp = 0.1
ki = 0.01

timing_correction, updated_integral = timing_loop_filter(
    timing_error,
    prev_integral_state,
    kp,
    ki
)

expected_integral = 0.052
expected_correction = 0.072

assert np.isclose(updated_integral, expected_integral)
assert np.isclose(timing_correction, expected_correction)

print("PI loop filter test passed!")
print(f"Updated integral: {updated_integral}")
print(f"Timing correction: {timing_correction}")


# ============================================================
# TEST 6: Fractional timing offset recovery
# ============================================================

print("\nTEST 6: Fractional timing offset recovery")

timing_offset = 0.5

sample_indices = np.arange(len(rx_filtered))

delayed_signal = (
    np.interp(
        sample_indices - timing_offset,
        sample_indices,
        rx_filtered.real,
        left=0,
        right=0
    )
    + 1j * np.interp(
        sample_indices - timing_offset,
        sample_indices,
        rx_filtered.imag,
        left=0,
        right=0
    )
)

kp = 0.01
ki = 0.0001

recovered = timing_recovery(
    delayed_signal,
    samples_per_symbol=samples_per_symbol,
    kp=kp,
    ki=ki
)

assert len(recovered) > 0
assert np.all(np.isfinite(recovered))

# Reference samples at actual delayed symbol centers
expected = np.array([
    interpolate_sample(
        delayed_signal,
        group_delay + timing_offset + k * samples_per_symbol
    )
    for k in range(len(recovered))
])

# Samples without timing correction
uncorrected = np.array([
    interpolate_sample(
        delayed_signal,
        group_delay + k * samples_per_symbol
    )
    for k in range(len(recovered))
])

mse_before = np.mean(np.abs(expected - uncorrected)**2)
mse_after = np.mean(np.abs(expected - recovered)**2)

improvement = (
    (mse_before - mse_after) / mse_before
) * 100

print("Fractional timing offset test completed!")
print(f"Introduced timing offset: {timing_offset} samples")
print(f"Kp: {kp}")
print(f"Ki: {ki}")
print(f"Recovered symbols: {len(recovered)}")
print(f"MSE before recovery: {mse_before:.8e}")
print(f"MSE after recovery: {mse_after:.8e}")
print(f"MSE improvement: {improvement:.2f}%")

assert mse_after < mse_before, (
    "Fractional timing recovery did not improve alignment"
)

print("Fractional timing recovery test passed!")


# ============================================================
# TEST 7: Clock-rate mismatch recovery
# ============================================================

print("\nTEST 7: Clock-rate mismatch recovery")

# Introduce a 500 ppm sample-rate mismatch.
# The output sampling interval is slightly shorter than
# the original sampling interval.

up_factor = 2000
down_factor = 2001

clock_scale = up_factor / down_factor

clock_mismatch_ppm = (
    (1 - clock_scale) * 1e6
)

clock_mismatch_signal = resample_poly(
    rx_filtered,
    up=up_factor,
    down=down_factor
)

print(f"Introduced clock mismatch: {clock_mismatch_ppm:.2f} ppm")
print(f"Original signal length: {len(rx_filtered)}")
print(f"Clock-mismatched signal length: {len(clock_mismatch_signal)}")

# Run timing recovery with the same loop gains
kp = 0.01
ki = 0.0001

recovered_clock = timing_recovery(
    clock_mismatch_signal,
    samples_per_symbol=samples_per_symbol,
    kp=kp,
    ki=ki
)

assert len(recovered_clock) > 0
assert np.all(np.isfinite(recovered_clock))

# The ideal symbol positions are scaled by the clock ratio.
# This accounts for the accumulating timing drift.

symbol_numbers = np.arange(len(symbols))

true_positions = (
    group_delay + symbol_numbers * samples_per_symbol
) * clock_scale

# Keep only reference positions where interpolation is valid.
valid_mask = true_positions < len(clock_mismatch_signal) - 1

true_positions = true_positions[valid_mask]

# Compare the same transmitted symbols in both cases.
num_compare = min(
    len(true_positions),
    len(recovered_clock),
    len(symbols)
)

true_positions = true_positions[:num_compare]

expected_clock = np.array([
    interpolate_sample(clock_mismatch_signal, position)
    for position in true_positions
])

# Receiver without timing correction:
# assumes exactly four samples per symbol.
uncorrected_clock = np.array([
    interpolate_sample(
        clock_mismatch_signal,
        group_delay + k * samples_per_symbol
    )
    for k in range(num_compare)
])

# Recovered symbols from the timing loop
recovered_clock_compare = recovered_clock[:num_compare]

mse_clock_before = np.mean(
    np.abs(expected_clock - uncorrected_clock)**2
)

mse_clock_after = np.mean(
    np.abs(expected_clock - recovered_clock_compare)**2
)

clock_improvement = (
    (mse_clock_before - mse_clock_after)
    / mse_clock_before
) * 100

# Theoretical accumulated timing drift across the packet
total_clock_drift = (
    (group_delay + (len(symbols) - 1) * samples_per_symbol)
    * (1 - clock_scale)
)

print("\n--- Clock-Rate Mismatch Results ---")
print(f"Symbols compared: {num_compare}")
print(f"Samples per symbol (actual): {samples_per_symbol * clock_scale:.6f}")
print(f"Theoretical accumulated drift: {total_clock_drift:.4f} samples")
print(f"MSE before recovery: {mse_clock_before:.8e}")
print(f"MSE after recovery: {mse_clock_after:.8e}")
print(f"MSE improvement: {clock_improvement:.2f}%")

assert mse_clock_after < mse_clock_before, (
    "Clock-rate mismatch recovery did not improve alignment"
)

print("Clock-rate mismatch test passed!")


# ============================================================
# FINAL TEST SUMMARY
# ============================================================

print("\n========================================")
print("ALL RECEIVER DSP TESTS COMPLETED!")
print("========================================")
