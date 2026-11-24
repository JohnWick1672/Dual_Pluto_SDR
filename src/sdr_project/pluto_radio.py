import adi 
class PlutoRadio:

    def __init__(self,uri, tx_gain, rx_gain):
        self.uri = uri
        self.center_frequency = 2.4e9
        self.sample_rate = 1e6
        self.rf_bandwidth = 1e6
        self.tx_gain = tx_gain
        self.rx_gain = rx_gain
        self.radio = adi.Pluto(uri = self.uri)

    def configure_tx(self):
        self.radio.tx_enabled_channels = [0]
        self.radio.tx_lo = self.center_frequency
        self.radio.sample_rate = self.sample_rate
        self.radio.tx_rf_bandwidth = self.rf_bandwidth
        self.radio.tx_hardwaregain_chan0 = self.tx_gain

    def configure_rx(self):
        self.radio.rx_enabled_channels = [0]
        self.radio.rx_lo = self.center_frequency
        self.radio.sample_rate = self.sample_rate
        self.radio.rx_rf_bandwidth = self.rf_bandwidth
        self.radio.gain_control_mode_chan0 = 'manual'
        self.radio.rx_hardwaregain_chan0 = self.rx_gain