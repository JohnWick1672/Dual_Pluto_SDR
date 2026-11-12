
import sys
sys.path.insert(0, "src")

import numpy as np

from sdr_project.modulation import bpsk_modulation
from sdr_project.demodulation import (
    bpsk_demodulation,
    bpsk_receiver_sync
)
from sdr_project.channel import (
    awgn_channel,
    phase_offset_channel,
    frequency_offset_channel
)
from sdr_project.metrics import calculate_ber


# --------------------------------------------------
# 1. Simulation parameters
# --------------------------------------------------

num_bits = 100000
sample_rate = 100000          # Hz
frequency_offset = 500        # Hz
phase_offset = np.pi / 3      # radians
snr_db = 0                    # dB


# --------------------------------------------------
# 2. Generate transmitted data
# --------------------------------------------------

bits = np.random.randint(0, 2, size=num_bits, dtype=np.uint8)


# --------------------------------------------------
# 3. Transmitter: BPSK modulation
# --------------------------------------------------

symbols = bpsk_modulation(bits)


# --------------------------------------------------
# 4. Channel: Apply impairments
# --------------------------------------------------

received_symbols = symbols.copy()

if phase_offset != 0:
    received_symbols = phase_offset_channel(
        received_symbols, phase_offset
    )

if frequency_offset != 0:
    received_symbols = frequency_offset_channel(
        received_symbols, frequency_offset, sample_rate
    )

if snr_db is not None:
    received_symbols = awgn_channel(received_symbols, snr_db)


# --------------------------------------------------
# 5. Receiver: Synchronization
# --------------------------------------------------

corrected_symbols, estimated_offset = bpsk_receiver_sync(
    received_symbols,
    sample_rate
)

print(f"Actual frequency offset:    {frequency_offset:.2f} Hz")
print(f"Estimated frequency offset: {estimated_offset:.2f} Hz")


# --------------------------------------------------
# 6. Receiver: BPSK demodulation
# --------------------------------------------------

measured_bits = bpsk_demodulation(corrected_symbols)


# --------------------------------------------------
# 7. Performance metrics
# --------------------------------------------------

ber = calculate_ber(bits, measured_bits)

print(f"Bit Error Rate: {ber:.6f}")
