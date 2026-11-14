import sys
sys.path.insert(0, "src")
from sdr_project.packet import REGULAR_TELEMETRY,EMERGENCY_TELEMETRY
from sdr_project.telemetry import generate_telemetry
from sdr_project.packet import build_packet
from sdr_project.packet import decode_packet
from sdr_project.telemetry import decode_telemetry
from sdr_project.packet_manager import PacketManager
from sdr_project.telemetry import determine_packet_type



# Initialize packet manager
manager = PacketManager()
manager.sequence_number = 254

# Generate and test 4 pairs of packets
for i in range(4):

    # Generate a random sequence of telemetry measurements

    telemetry_stream = generate_telemetry()

    # Construct regular and emergency packets
    packet = manager.create_packet(
        packet_type= determine_packet_type(telemetry_stream),
        payload=telemetry_stream
    )

    # Decode packet
    packet_type, seq, payload = decode_packet(packet)

    # Decode telemetry payloads
    telemetry = decode_telemetry(payload)

    # Display packet information
    print(f"\nIteration {i + 1}")

    print("\nPacket")
    print(f"Packet Type: {packet_type}")
    print(f"Sequence Number: {seq}")
    print(f"Payload Matches: {payload == telemetry_stream}")

    print(f"Temperature: {telemetry['temperature']:.2f} °C")
    print(f"Battery: {telemetry['battery']} %")
    print(f"Voltage: {telemetry['voltage']:.2f} V")
    print(f"Current: {telemetry['current']:.2f} A")