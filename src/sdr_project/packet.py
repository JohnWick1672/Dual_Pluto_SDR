PREAMBLE = bytes.fromhex("AA CC F0 0F")
REGULAR_TELEMETRY = 0
EMERGENCY_TELEMETRY = 1

def build_packet(packet_type, sequence_number, payload):

    """
    Construct a telemetry packet.

    Packet structure:
    [PREAMBLE][HEADER][PAYLOAD][CRC]
    """

    # Convert payload into bytes
    payload = bytes(payload)

    # Construct header
    header = (
        packet_type.to_bytes(1, byteorder='big') +
        sequence_number.to_bytes(1, byteorder='big') +
        len(payload).to_bytes(2, byteorder='big')
    )

    # Combine preamble, header, and payload,crc
    packet_data = header + payload

    crc = calculate_crc(packet_data)

    packet = PREAMBLE + packet_data + crc.to_bytes(2,byteorder='big')

    return packet

def calculate_crc(data):

    #placeholder for crc
    crc = 0xFFFF

    for byte in data:
        #insert each byte into the upper 8 bits
        crc ^= (byte << 8)
        #break down bytes
        for bit in range(8):

            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
            #Keep CRC at 16 bits
            crc &= 0xFFFF
    return crc
            
def decode_packet(packet):

    #put packet into byte form
    packet = bytes(packet)

    #Check the PREAMBLE
    if not packet.startswith(PREAMBLE):
        raise ValueError("Invalid Packet Preamble")


    #ensuring the packet has at least 8 bytes
    if len(packet) < 8:
        raise ValueError('Header must be 4 bytes long')

    #extract the header
    header = packet[4:8]

    packet_type = header[0]
    sequence_number = header[1]
    payload_length = int.from_bytes(header[2:4],byteorder= "big")

    #payload stream starts after the first 8 bytes
    payload_start = 8
    payload_end = payload_start + payload_length

    #Checking whether the packet contains at least payload_end bytes
    if len(packet) < payload_end:
        raise ValueError('Incomplete Packet Payload')
    
    #actual payload data extracted from packet
    payload = packet[payload_start:payload_end]

    
    #now to extract the crc
    crc_end = payload_end +2
    #verify crc length
    if len(packet) < crc_end:
        raise ValueError('Missing or incomplete CRC')
    if len(packet) > crc_end:
        raise ValueError('Packet transmission exceeds expected length')

    received_crc = int.from_bytes(packet[payload_end:crc_end], byteorder= 'big')

    #calculate our crc from recieved data and compare to transmitted
    calculated_crc = calculate_crc(packet[4:payload_end])

    if received_crc != calculated_crc:
        raise ValueError('CRC verification failed')

    return packet_type, sequence_number,payload

