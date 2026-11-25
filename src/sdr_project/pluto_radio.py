import adi
import numpy as np 
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

    def transmit(self,tx_samples, cyclic_transmission):
        #Input validation
        if not isinstance(tx_samples,np.ndarray):
            raise TypeError('Transmit data must be numpy array data type')
        if not np.iscomplexobj(tx_samples):
            raise ValueError('Transmit data must be complex')
        if not np.all(np.isfinite(tx_samples)):
            raise ValueError('Input must be finite')
        if tx_samples.size == 0:
            raise ValueError('Size of transmit data cant be zero')
        #Cyclic transmission is boolean, true is for continuous transmission
        self.radio.tx_cyclic_buffer = cyclic_transmission
        self.radio.tx(tx_samples)

    def receive(self):
        #Received samples
        rx_samples = self.radio.rx()
        #ensure working with complex numpy arrays
        rx_samples = np.array(rx_samples,dtype = np.complex64)

        return rx_samples


    def close(self):
        try:
            self.radio.tx_destroy_buffer()
        except Exception:
            pass
        try:
            self.radio.rx_destroy_buffer()
        except Exception:
            pass