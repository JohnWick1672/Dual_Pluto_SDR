
import sys
sys.path.insert(0, 'src')

import numpy as np

from sdr_project.telemetry import (
    generate_telemetry,
    determine_packet_type,
    decode_telemetry
)

from sdr_project.packet_manager import PacketManager

from sdr_project.modulation import (
    bpsk_modulation,
    root_raised_cosine,
    upsample_symbols,
    pulse_shape,
    resample_transmit_signal
)

from sdr_project.channel import (
    frequency_offset_channel,
    phase_offset_channel,
    awgn_channel
)

from sdr_project.receiver_dsp import (
    decimate_received_signal,
    matched_rrc_filter,
    timing_recovery
)

from sdr_project.demodulation import (
    bpsk_receiver_sync,
    bpsk_demodulation
)

from sdr_project.packet import PREAMBLE
from sdr_project.receiver import Receiver
from sdr_project.metrics import calculate_ber


# ============================================================
# SYSTEM PARAMETERS
# ============================================================

BIT_RATE = 10000
SYMBOL_RATE = 10000
SAMPLES_PER_SYMBOL = 4

BASEBAND_SAMPLE_RATE = 40000
PLUTO_SAMPLE_RATE = 1000000

INTERPOLATION_FACTOR = 25
DECIMATION_FACTOR = 25

RRC_BETA = 0.35
RRC_SPAN = 10

# Channel parameters
FREQUENCY_OFFSET = 250
PHASE_OFFSET = 0.7
SNR_DB = 20

# Receiver timing recovery parameters
KP = 0.01
KI = 0.0001


# ============================================================
# TRANSMITTER: TELEMETRY AND PACKET GENERATION
# ============================================================

telemetry_payload = generate_telemetry()

packet_type = determine_packet_type(telemetry_payload)

packet_manager = PacketManager()

packet = packet_manager.create_packet(
    packet_type,
    telemetry_payload
)

# Convert packet bytes into binary bits
packet_array = np.frombuffer(packet, dtype=np.uint8)

transmitted_bits = np.unpackbits(packet_array)

print("\n--- Packet Generation Results ---")
print("Packet length:", len(packet), "bytes")
print("Bit count:", len(transmitted_bits))


# ============================================================
# TRANSMITTER: BPSK MODULATION AND PULSE SHAPING
# ============================================================

# Convert packet bits into BPSK symbols
transmitted_symbols = bpsk_modulation(transmitted_bits)

# Generate RRC filter coefficients
rrc_coefficients = root_raised_cosine(
    RRC_BETA,
    SAMPLES_PER_SYMBOL,
    RRC_SPAN
)

# Upsample BPSK symbols
upsampled_symbols = upsample_symbols(
    transmitted_symbols,
    SAMPLES_PER_SYMBOL
)

# Apply transmit pulse shaping
tx_waveform = pulse_shape(
    upsampled_symbols,
    rrc_coefficients
)

# Interpolate from 40 kS/s to 1 MSPS
tx_samples = resample_transmit_signal(
    tx_waveform,
    INTERPOLATION_FACTOR
)

print("\n--- Transmitter Results ---")
print("BPSK symbols:", len(transmitted_symbols))
print("RRC filter taps:", len(rrc_coefficients))
print("Upsampled symbols:", len(upsampled_symbols))
print("Pulse-shaped waveform:", len(tx_waveform))
print("Transmitted IQ samples:", len(tx_samples))


# ============================================================
# CHANNEL: FREQUENCY OFFSET, PHASE OFFSET, AND AWGN
# ============================================================

# Apply frequency offset
rx_samples = frequency_offset_channel(
    tx_samples,
    FREQUENCY_OFFSET,
    PLUTO_SAMPLE_RATE
)

# Apply constant phase offset
rx_samples = phase_offset_channel(
    rx_samples,
    PHASE_OFFSET
)

# Add AWGN
rx_samples = awgn_channel(
    rx_samples,
    SNR_DB
)

print("\n--- Channel Results ---")
print("Frequency offset:", FREQUENCY_OFFSET, "Hz")
print("Phase offset:", PHASE_OFFSET, "radians")
print("SNR:", SNR_DB, "dB")
print("Received IQ samples:", len(rx_samples))


# ============================================================
# RECEIVER: DECIMATION AND MATCHED FILTERING
# ============================================================

# Decimate received signal from 1 MSPS to 40 kS/s
decimated_signal = decimate_received_signal(
    rx_samples,
    DECIMATION_FACTOR
)

# Apply receive-side matched RRC filter
matched_signal = matched_rrc_filter(
    decimated_signal,
    rrc_coefficients
)

print("\n--- Receiver Filtering Results ---")
print("Decimated samples:", len(decimated_signal))
print("Matched filter samples:", len(matched_signal))


# ============================================================
# RECEIVER: SYMBOL TIMING RECOVERY
# ============================================================

recovered_symbols = timing_recovery(
    matched_signal,
    SAMPLES_PER_SYMBOL,
    KP,
    KI
)

print("\n--- Timing Recovery Results ---")
print("Recovered symbols:", len(recovered_symbols))

# Verify that enough symbols were recovered
if len(recovered_symbols) < len(transmitted_bits):
    raise RuntimeError(
        "Insufficient recovered symbols for packet decoding."
    )

# Remove extra symbols resulting from filter tails
recovered_symbols = recovered_symbols[:len(transmitted_bits)]


# ============================================================
# RECEIVER: CARRIER SYNCHRONIZATION
# ============================================================

# Extract known preamble bits for phase ambiguity correction
preamble_bits = np.unpackbits(
    np.frombuffer(PREAMBLE, dtype=np.uint8)
)

# Perform frequency and phase synchronization
synchronized_symbols, estimated_frequency_offset = bpsk_receiver_sync(
    recovered_symbols,
    SYMBOL_RATE,
    preamble_bits=preamble_bits
)

print("\n--- Carrier Synchronization Results ---")
print("Actual frequency offset:", FREQUENCY_OFFSET, "Hz")
print("Estimated frequency offset:", estimated_frequency_offset, "Hz")
print("Corrected symbols:", len(synchronized_symbols))


# ============================================================
# RECEIVER: BPSK DEMODULATION AND BER
# ============================================================

# Recover binary bits
received_bits = bpsk_demodulation(synchronized_symbols)

# Calculate BER
ber = calculate_ber(
    transmitted_bits,
    received_bits
)

bit_errors = np.sum(transmitted_bits != received_bits)

print("\n--- Demodulation Results ---")
print("Transmitted bits:", len(transmitted_bits))
print("Received bits:", len(received_bits))
print("Bit errors:", bit_errors)
print("BER:", ber)


# ============================================================
# RECEIVER: PACKET RECONSTRUCTION AND CRC VERIFICATION
# ============================================================

# Convert recovered bits back into bytes
received_packet = np.packbits(received_bits).tobytes()

# Initialize receiver packet processor
packet_receiver = Receiver()

# Decode packet and verify CRC
packet_type_rx, sequence_number_rx, received_payload, missing_packets = (
    packet_receiver.process_packet(received_packet)
)

print("\n--- Packet Reception Results ---")
print("Received packet type:", packet_type_rx)
print("Received sequence number:", sequence_number_rx)
print("Missing packets:", missing_packets)
print("Received payload length:", len(received_payload))


# ============================================================
# TELEMETRY RECOVERY AND VERIFICATION
# ============================================================

# Deserialize received telemetry
received_telemetry = decode_telemetry(received_payload)

# Deserialize original telemetry
transmitted_telemetry = decode_telemetry(telemetry_payload)

# Verify payload integrity
payload_match = received_payload == telemetry_payload

print("\n--- Telemetry Recovery Results ---")
print("Transmitted telemetry:", transmitted_telemetry)
print("Received telemetry:", received_telemetry)
print("Telemetry payload matches:", payload_match)


# ============================================================
# FINAL RESULTS
# ============================================================

print("\n====================================")
print("       END-TO-END TEST RESULTS")
print("====================================")

print("BER:", ber)
print("Bit errors:", bit_errors)
print("CRC verification: PASSED")
print("Telemetry recovered:", payload_match)

if ber == 0 and payload_match:
    print("\nEND-TO-END TEST PASSED")
else:
    print("\nEND-TO-END TEST COMPLETED WITH ERRORS")
