class PacketManager:
    """"
    Manage packet sequence numbers for telemetry transmission.
    """
    def __init__(self):
        """"
        Initialize the packet manager with a sequence number of zero
        """
        self.sequence_number = 0

    def get_next_sequence_number(self):
        """"
        Return the current sequence number and increment it

        Returns:
            int: Current packet sequence number (0-255)
        """
        
        current_seq_num = self.sequence_number

        if (current_seq_num+1) % 256 == 0:
            self.sequence_number = 0
        else:
            self.sequence_number += 1

        return current_seq_num


