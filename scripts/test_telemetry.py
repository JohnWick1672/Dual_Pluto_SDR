import sys
sys.path.insert(0, "src")

from sdr_project.telemetry import generate_telemetry
from sdr_project.packet import build_packet
from sdr_project.packet import decode_packet
from sdr_project.telemetry import decode_telemetry
from sdr_project.packet_manager import PacketManager


#Generate a random sequence of measurements
telemetry_stream = generate_telemetry()

#build_packet from payload data
packet = build_packet(packet_type=0, sequence_number=0, payload= telemetry_stream)

packet_type,sequence_number, decoded_payload = decode_packet(packet)

print(packet_type)
print(sequence_number)
print(decoded_payload)


recovered_telemetry = decode_telemetry(decoded_payload)
print(f"Timestamp: {recovered_telemetry['timestamp']}")
print(f"Temperature: {recovered_telemetry['temperature']} F")
print(f"Battery:  {recovered_telemetry['battery']} %")
print(f"Voltage:  {recovered_telemetry['voltage']} V")
print(f"Current:  {recovered_telemetry['current']} A")

manager = PacketManager()
manager.sequence_number = 254

for i in range(4):
    print(manager.get_next_sequence_number())

    