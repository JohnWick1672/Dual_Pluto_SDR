import sys
sys.path.insert(0,'src')
from sdr_project.packet import PREAMBLE, build_packet,decode_packet
import numpy as np
from sdr_project.telemetry import generate_telemetry,determine_packet_type


def find_preamble(received_bits):
    """
    Find the preamble in a stream of bits after BPSK demod

    Parameters:
        received_bits: Bit sequence to parse

    Returns:
    The starting index of the known preamble in the sequence of bits and the received stream in bit form
    """
    #Convert preamble from bytes to bits
    preamble = np.frombuffer(PREAMBLE, dtype=np.uint8)
    preamble_bits = np.unpackbits(preamble)

    len_preamble = len(preamble_bits)
    len_received_bits = len(received_bits)
    

    #input validation
    received_bits = np.array(received_bits)
    if not received_bits.size >= len_preamble:
        raise ValueError('Input stream must be longer than 32 bits')
    if not np.all(np.isin(received_bits,[0,1])):
        raise ValueError('Received stream must contain only binary values')
    
    #Loop through all possible starting positions
    for i in range(len_received_bits - len_preamble +1):
        if np.array_equal(preamble_bits,received_bits[i:i+len_preamble]):
            return i

    return None

def extract_packet(received_bits, preamble_index):
    """
    Takes in the stream of received bits and a packet index. The preamble index serves to extract the full packet at that starting point

    Parameters:
        received_bits(numpy array): Stream of received bits 
        preamble_index(int): index that marks the start of the preable in the received bits

    Returns:
        packet(byte): packet in byte form
    """
    #small validation check
    if not isinstance(preamble_index, (int, np.integer)):
        raise TypeError('Preamble index must be an integer')
    if preamble_index < 0:
        raise ValueError('Preamble index must be greater than or equal to zero')
    #for current packet format 216 is the length of the packet in bit format
    end_packet_length = preamble_index + 216

    #check to see if we have enough bits to extract a full packet
    if end_packet_length > len(received_bits):
        raise IndexError('Not enough bits to extract a full packet')

    bit_packet = received_bits[preamble_index:end_packet_length]
    byte_packet = np.packbits(bit_packet).tobytes()
    return byte_packet


#=========TEST==========
#=======================

# Random measurements
payload = generate_telemetry()

# Determine packet type
packet_type = determine_packet_type(payload)

packet = build_packet(packet_type, 0, payload)

# Unpack into bits
packet_bytes = np.frombuffer(packet, dtype=np.uint8)
packet_bits = np.unpackbits(packet_bytes)

# Add random bits before packet
random_bits = np.array([1, 0, 1, 1, 1, 1])
final_bit_stream = np.append(random_bits, packet_bits)

# Extract preamble index
index= find_preamble(final_bit_stream)

if index is None:
    raise ValueError("No preamble detected")

final_packet = extract_packet(final_bit_stream, index)

# Create a corrupted copy of the extracted packet
corrupted_packet = bytearray(final_packet)

# Flip one bit in the payload
# Bytes 0-3: preamble
# Bytes 4-7: header
# Bytes 8-24: payload
# Bytes 25-26: CRC
corrupted_packet[10] ^= 0b00000001

# Verify preamble was not changed
print("Preamble unchanged:", corrupted_packet[:4] == final_packet[:4])

# Attempt to decode corrupted packet
try:
    decode_packet(bytes(corrupted_packet))
    print("ERROR: Corrupted packet was not detected")
except ValueError as e:
    print("Corrupted packet successfully rejected:", e)

print("\nDetected preamble index:", index)

print("Original packet length:", len(packet), "bytes")
print("Extracted packet length:", len(final_packet), "bytes")

print("Original packet:", packet)
print("Extracted packet:", final_packet)

# Decode original extracted packet
decoded_type, decoded_sequence, decoded_payload = decode_packet(final_packet)

print("Decoded packet type:", decoded_type)
print("Decoded sequence number:", decoded_sequence)
print("Decoded payload:", decoded_payload)

# Verify successful extraction
print("Packet extraction successful:", final_packet == packet)
print("Payload matches original:", decoded_payload == payload)
print("Original CRC verification: PASSED")
