import sys
sys.path.insert(0, "src")

from sdr_project.telemetry import (
    generate_telemetry,
    decode_telemetry,
    determine_packet_type
)
from sdr_project.packet_manager import PacketManager
from sdr_project.receiver import Receiver


# ===================================
# TRANSMITTER
# ===================================

manager = PacketManager()
manager.sequence_number = 254

transmitted_packets = []

print("\n========== TRANSMITTER ==========")

# Generate and construct 4 telemetry packets
for i in range(4):

    # Generate telemetry
    telemetry_stream = generate_telemetry()

    # Classify telemetry
    packet_type = determine_packet_type(telemetry_stream)

    # Construct packet
    packet = manager.create_packet(
        packet_type=packet_type,
        payload=telemetry_stream
    )

    transmitted_packets.append(packet)

    # Display transmitted telemetry
    telemetry = decode_telemetry(telemetry_stream)

    print(f"\nTransmitted Packet {i + 1}")
    print(f"Packet Type: {packet_type}")
    print(f"Temperature: {telemetry['temperature']:.2f} °C")
    print(f"Battery: {telemetry['battery']} %")
    print(f"Voltage: {telemetry['voltage']:.2f} V")
    print(f"Current: {telemetry['current']:.2f} A")


# ===================================
# CHANNEL: SIMULATED PACKET LOSS
# ===================================

# Drop the third transmitted packet
received_packets = transmitted_packets[:2] + transmitted_packets[3:]


# ===================================
# RECEIVER
# ===================================

receiver = Receiver()

received_sequence_numbers = []

print("\n========== RECEIVER ==========")

for i, packet in enumerate(received_packets):

    # Decode packet and process sequence number
    packet_type, sequence_number, payload, missing = receiver.process_packet(packet)

    received_sequence_numbers.append(sequence_number)

    # Recover telemetry
    telemetry = decode_telemetry(payload)

    print(f"\nReceived Packet {i + 1}")
    print(f"Packet Type: {packet_type}")
    print(f"Sequence Number: {sequence_number}")
    print(f"Newly Missing: {missing}")
    print(f"Temperature: {telemetry['temperature']:.2f} °C")
    print(f"Battery: {telemetry['battery']} %")
    print(f"Voltage: {telemetry['voltage']:.2f} V")
    print(f"Current: {telemetry['current']:.2f} A")


# ===================================
# FINAL INTEGRATION RESULTS
# ===================================

print("\n========== LINK SUMMARY ==========")

print(f"Packets Transmitted: {len(transmitted_packets)}")
print(f"Packets Received: {len(received_packets)}")
print(f"Packets Lost: {receiver.total_missing_packets}")

print(f"Received Sequence Numbers: {received_sequence_numbers}")

# Verify expected results
assert len(transmitted_packets) == 4
assert len(received_packets) == 3
assert received_sequence_numbers == [254, 255, 1]
assert receiver.total_missing_packets == 1

print("\nSUCCESS: End-to-end telemetry test passed!")