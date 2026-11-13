import sys
sys.path.insert(0, "src")

from sdr_project.telemetry import generate_telemetry
from sdr_project.packet import build_packet
from sdr_project.packet import decode_packet
from sdr_project.telemetry import decode_telemetry
from sdr_project.packet_manager import PacketManager



# Generate a random sequence of telemetry measurements
telemetry_stream = generate_telemetry()

# Initialize packet manager
manager = PacketManager()
manager.sequence_number = 254
# Generate and test 4 consecutive packets
for i in range(4):

    # Construct packet with automatically assigned sequence number
    packet = manager.create_packet(packet_type=0, payload=telemetry_stream)

    # Decode the packet
    packet_type, sequence_number, decoded_payload = decode_packet(packet)

    # Decode the telemetry payload
    recovered_telemetry = decode_telemetry(decoded_payload)

    # Display packet information
    print(f"\nPacket {i + 1}")
    print(f"Packet Type: {packet_type}")
    print(f"Sequence Number: {sequence_number}")
    print(f"Payload Matches: {decoded_payload == telemetry_stream}")

    print(f"Timestamp: {recovered_telemetry['timestamp']}")
    print(f"Temperature: {recovered_telemetry['temperature']:.2f} °C")
    print(f"Battery: {recovered_telemetry['battery']} %")
    print(f"Voltage: {recovered_telemetry['voltage']:.2f} V")
    print(f"Current: {recovered_telemetry['current']:.2f} A")
