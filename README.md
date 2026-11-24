# Dual-Pluto SDR CubeSat Telemetry Communications System

A Python-based digital communications project using two ADALM-Pluto SDRs to simulate a CubeSat-to-ground-station telemetry link.

## Project Overview

The goal of this project is to build and characterize a packet-based wireless communications link between two software-defined radios (SDRs).

One Pluto SDR will act as the simulated CubeSat transmitter, while the second will act as the ground-station receiver. The transmitter generates spacecraft telemetry, encodes it into packets, modulates the data, and transmits it. The receiver captures the signal, recovers the transmitted bits, validates packets, and decodes the telemetry.

The primary modulation scheme is **Binary Phase Shift Keying (BPSK)**. The communications chain will first be validated in software before integrating the SDR hardware.

## System Architecture

### Transmitter

1. Generate simulated CubeSat telemetry.
2. Serialize telemetry measurements into a binary payload.
3. Determine the packet type based on telemetry thresholds.
4. Construct a packet containing a preamble, header, payload, and CRC.
5. Assign a sequence number to each packet.
6. Convert packet bits into BPSK symbols.
7. Apply pulse shaping and prepare the waveform for transmission.
8. Transmit the complex IQ waveform using the Pluto SDR.

### Receiver

1. Capture complex IQ samples using the second Pluto SDR.
2. Decimate the received signal to the baseband processing sample rate.
3. Apply receive-side matched RRC filtering.
4. Recover symbol timing using Gardner timing recovery.
5. Correct carrier frequency offset and phase using the existing synchronization algorithms.
6. Recover the transmitted BPSK symbols and bits.
7. Detect packet boundaries using the preamble.
8. Decode the packet header and payload.
9. Verify packet integrity using the CRC.
10. Track packet sequence numbers and identify missing packets.
11. Deserialize and display the recovered telemetry.

## Telemetry Format

The telemetry generator currently simulates the following measurements:

| Field       | Description                      | Current simulation range |
| ----------- | -------------------------------- | ------------------------ |
| Timestamp   | Unix timestamp                   | Current system time      |
| Temperature | Simulated spacecraft temperature | 15–30 °C                 |
| Battery     | Simulated battery level          | 40–100%                  |
| Voltage     | Simulated bus voltage            | 5.0–8.4 V                |
| Current     | Simulated current consumption    | 0.5–1.5 A                |

The telemetry values are illustrative simulation values, not flight-system specifications.

Telemetry is serialized into a 17-byte binary payload using Python's `struct` module. The receiver can deserialize the payload into readable measurements.

The transmitter also classifies telemetry packets as regular or emergency based on predefined measurement thresholds.

## Packet Protocol

The current packet format is:

| Field    | Size     | Description                                  |
| -------- | -------- | -------------------------------------------- |
| Preamble | 4 bytes  | `AA CC F0 0F`                                |
| Header   | 4 bytes  | Packet type, sequence number, payload length |
| Payload  | Variable | Serialized telemetry data                    |
| CRC      | 2 bytes  | CRC-16-CCITT-FALSE                           |

The header contains:

- **Packet type:** Identifies the packet category.
- **Sequence number:** Identifies the packet sequence, ranging from 0 to 255 before rollover.
- **Payload length:** Specifies the payload size in bytes, encoded big-endian.

The CRC uses CRC-16-CCITT-FALSE parameters:

- Polynomial: `0x1021`
- Initial value: `0xFFFF`
- Final XOR: `0x0000`
- CRC coverage: Header and payload; the preamble is excluded.

The receiver verifies the CRC before accepting the decoded payload. The CRC detects corrupted packets; it does not correct transmission errors.

The receiver also tracks sequence numbers to identify missing and duplicate packets.

## Modulation and Signal Processing

BPSK is the primary modulation scheme.

The current symbol mapping is:

| Input bit | BPSK symbol |
| --------- | ----------- |
| 0         | +1 + 0j     |
| 1         | -1 + 0j     |

The software currently includes:

- BPSK modulation and hard-decision demodulation
- AWGN, phase-offset, and frequency-offset channel models
- Frequency-offset estimation and correction
- Costas-loop carrier phase tracking
- BER calculation
- RRC pulse shaping and waveform generation
- Polyphase interpolation and decimation
- Matched RRC filtering
- Gardner timing error detection
- PI timing loop filtering
- Closed-loop symbol timing recovery

## Current Development Status

### Implemented and tested

- [x] Python project structure and development environment
- [x] BPSK modulation and basic demodulation
- [x] AWGN, phase-offset, and frequency-offset channel models
- [x] Initial carrier frequency and phase correction
- [x] Costas-loop carrier phase tracking
- [x] BER calculation
- [x] Telemetry generation and binary serialization
- [x] Telemetry deserialization into readable measurements
- [x] Telemetry-based regular/emergency packet classification
- [x] Packet construction with preamble and header
- [x] CRC-16-CCITT-FALSE calculation and verification
- [x] Packet decoding and payload recovery
- [x] Automatic packet sequence numbering and rollover
- [x] Receiver-side sequence tracking and duplicate detection
- [x] Packet-loss detection and cumulative packet-loss tracking
- [x] Testing of multiple packets and packet sequence rollover
- [x] End-to-end telemetry test with simulated packet loss
- [x] Root-raised-cosine (RRC) filter coefficient generation
- [x] BPSK symbol upsampling (4 samples per symbol)
- [x] RRC pulse shaping through digital convolution
- [x] Time-domain and frequency-domain waveform inspection
- [x] Sample-rate conversion from 40 kS/s to 1 MSPS (25× interpolation)
- [x] Validation of complex IQ waveform generation
- [x] Spectral comparison before and after interpolation
- [x] Initial occupied-bandwidth estimation
- [x] Receive-side decimation from 1 MSPS to 40 kS/s
- [x] Receive-side matched RRC filtering
- [x] Linear interpolation for fractional sample positions
- [x] Gardner timing error detector
- [x] PI timing loop filter
- [x] Closed-loop symbol timing recovery
- [x] Fractional timing-offset recovery in simulation
- [x] Sample-clock mismatch recovery in simulation

### Planned development

- [ ] Integrate existing frequency-offset estimation and correction into the oversampled receiver chain
- [ ] Integrate the existing Costas loop into the oversampled receiver chain
- [ ] Complete end-to-end BPSK waveform simulation
- [ ] Implement preamble-based packet acquisition and synchronization
- [ ] Validate end-to-end BER and packet error rate (PER) under simulated channel conditions
- [ ] Integrate both ADALM-Pluto SDRs
- [ ] Demonstrate packet transmission and telemetry recovery over the RF link
- [ ] Characterize BER, packet error rate (PER), EVM, throughput, and goodput under controlled channel conditions

## Hardware and Software

### Hardware

- 2 × Analog Devices ADALM-Pluto SDR
- RF cables, SMA adapters, and attenuators for controlled conducted testing
- External antennas for the over-the-air demonstration
- VNA access for passive RF component and antenna characterization

The intended RF operating frequency is 2.4 GHz, using two custom microstrip patch antennas.

### Software

- Python
- NumPy
- SciPy
- Matplotlib
- Pandas
- Pytest
- IPykernel
- Visual Studio Code

The Pluto SDR hardware interface and associated software dependencies will be added during hardware integration.

## Project Structure

```text
Dual_Pluto_SDR/
│
├── src/
│   └── sdr_project/
│       ├── __init__.py
│       ├── modulation.py
│       ├── channel.py
│       ├── demodulation.py
│       ├── metrics.py
│       ├── packet.py
│       ├── telemetry.py
│       ├── packet_manager.py
│       ├── receiver.py
│       └── receiver_dsp.py
│
├── scripts/
│   ├── plot_bpsk.py
│   ├── plot_tx_waveform.py
│   ├── test_link.py
│   ├── test_telemetry.py
│   ├── test_resampling.py
│   └── test_receiver_dsp.py
│
├── tests/
├── data/
├── requirements.txt
├── README.md
└── .gitignore