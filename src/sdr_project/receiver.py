from .packet import decode_packet
class Receiver:

    def __init__(self):
        self.expected_sequence = None
        self.missing_packets = 0
        self.last_sequence_number = None
        self.received_sequences = set()
        self.total_missing_packets = 0

    def process_sequence(self,sequence_number):
        """
        Process an incoming packet sequence number and determine whether any packets have been missed.

        Parameters:
            sequence_number(int): The sequence number extraced from the recieved packet header.
        
        Returns:
            int: Number of packets missed since the previous successfully recieved packet.
        """
        #Duplicate check
        if sequence_number in self.received_sequences:
            return 0

        # initializing packet sequencing 
        if self.expected_sequence is None:

            #updating last_seq_num received and updating set of sequence numbers recieved
            self.received_sequences.add(sequence_number)
            self.last_sequence_number = sequence_number
            self.expected_sequence = (sequence_number + 1) % 256
            return 0
        
        # reporting any mismatches between expected and recieved
        else:
            self.missing_packets = (sequence_number - self.expected_sequence) % 256
            self.total_missing_packets += self.missing_packets
            self.expected_sequence = (sequence_number + 1) % 256

            #updating last_seq_num and set of sequence numbers
            self.received_sequences.add(sequence_number)
            self.last_sequence_number = sequence_number

            return self.missing_packets


    def process_packet(self,packet):
        """
        Decode an incoming packet, extract its information, and
        determine how many packets were missed.

        Parameters:
           packet (bytes): The fully constructed telemetry packet.

        Returns:
            tuple: Contains packet_type, sequence_number, payload, and missing packets
          
        """
        #Extract packet information
        packet_type,seq_num, payload = decode_packet(packet)

        # process the sequence and calculate missing packets
        missing = self.process_sequence(seq_num)

        return (packet_type,seq_num,payload,missing)







