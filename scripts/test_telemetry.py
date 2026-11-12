import sys
sys.path.insert(0, "src")

from sdr_project.telemetry import generate_telemetry
from sdr_project.packet import build_packet
from sdr_project.packet import decode_packet


#Generate a random sequence of measurements
telemetry_stream = generate_telemetry()

#build_packet from payload data
packet = build_packet(packet_type=0, sequence_number=0, payload= telemetry_stream)

packet_type,sequence_number, decoded_payload = decode_packet(packet)

print(packet_type)
print(sequence_number)
print(decoded_payload)

print(telemetry_stream == decoded_payload)