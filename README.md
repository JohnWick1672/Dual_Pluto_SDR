# Dual-Pluto SDR CubeSat Telemetry Communications System

A Python-based digital communications project using two ADALM-Pluto SDRs to simulate a CubeSat-to-ground-station telemetry link.

## Project Overview

The goal of this project is to build and characterize a packet-based wireless communications link between two software-defined radios (SDRs).

One Pluto SDR will act as the simulated CubeSat transmitter, while the second will act as the ground-station receiver. The transmitter will generate spacecraft telemetry, encode it into packets, modulate the data, and transmit it. The receiver will capture the signal, recover the transmitted bits, validate the packets, and decode the telemetry.

The primary modulation scheme is **Binary Phase Shift Keying (BPSK)**. The project will first validate the communications chain in software before integrating the SDR hardware.

## System Architecture

### Transmitter

1. Generate simulated CubeSat telemetry.
2. Serialize telemetry measurements into a binary payload.
3. Construct a packet containing a preamble, header, payload, and CRC.
4. Convert packet bits into BPSK symbols.
5. Apply pulse shaping and prepare the waveform for transmission.
6. Transmit the complex IQ waveform using the Pluto SDR.

### Receiver

1. Capture complex IQ samples using the second Pluto SDR.
2. Apply receive filtering and synchronization.
3. Recover the transmitted BPSK symbols and bits.
4. Detect packet boundaries using the preamble.
5. Decode the packet header and payload.
6. Verify packet integrity using the CRC.
7. Deserialize and display the recovered telemetry.

## Telemetry Format

The current telemetry generator simulates the following measurements:

| Field | Description | Current simulation range |
|---|---|---|
| Timestamp | Unix timestamp | Current system time |
| Temperature | Simulated spacecraft temperature | 20–30 °C |
| Battery | Simulated battery level | 80–100% |
| Voltage | Simulated bus voltage | 7.0–8.4 V |
| Current | Simulated current consumption | 0.5–1.2 A |

The telemetry values are illustrative simulation values, not flight-system specifications.

Telemetry is serialized into a 17-byte binary payload using Python's `struct` module.

## Packet Protocol

The current packet format is:

| Field | Size | Description |
|---|---:|---|
| Preamble | 4 bytes | `AA CC F0 0F` |
| Header | 4 bytes | Packet type, sequence number, payload length |
| Payload | Variable | Serialized telemetry data |
| CRC | 2 bytes | CRC-16-CCITT-FALSE |

The header contains:

- **Packet type:** Identifies the packet category.
- **Sequence number:** Identifies the packet sequence.
- **Payload length:** Specifies the payload size in bytes, encoded big-endian.

The CRC uses CRC-16-CCITT-FALSE parameters:

- Polynomial: `0x1021`
- Initial value: `0xFFFF`
- Final XOR: `0x0000`
- CRC coverage: Header and payload; the preamble is excluded.

The receiver checks the CRC before accepting the decoded payload. The CRC detects corrupted packets; it does not correct transmission errors.

## Modulation and Signal Processing

BPSK is the primary modulation scheme.

The current symbol mapping is:

| Input bit | BPSK symbol |
|---|---|
| 0 | +1 + 0j |
| 1 | -1 + 0j |

The software currently includes:

- BPSK modulation and hard-decision demodulation
- Additive white Gaussian noise (AWGN) channel model
- Phase-offset channel model
- Frequency-offset channel model
- Initial frequency-offset estimation and correction
- Basic Costas-style phase tracking
- Bit error rate (BER) calculation

The current synchronization implementation is an initial symbol-rate simulation. Pulse shaping, oversampled waveform processing, matched filtering, packet acquisition, and timing recovery are still under development.

## Current Development Status

### Implemented and tested

- [x] Python project structure and development environment
- [x] BPSK modulation and basic demodulation
- [x] AWGN, phase-offset, and frequency-offset channel models
- [x] Initial carrier frequency and phase correction
- [x] BER calculation
- [x] Telemetry generation and binary serialization
- [x] Packet construction with preamble and header
- [x] CRC-16-CCITT-FALSE calculation and verification
- [x] Packet decoding and payload recovery
- [x] End-to-end software test: telemetry generation → packet construction → packet decoding → payload recovery

The end-to-end packet test confirmed that the recovered payload matched the original serialized telemetry payload byte-for-byte.

### Planned development

- [ ] Deserialize recovered telemetry into readable measurements
- [ ] Implement automatic packet sequence numbering
- [ ] Test multiple packets and packet types
- [ ] Implement root-raised-cosine (RRC) pulse shaping
- [ ] Add oversampling and matched filtering
- [ ] Implement packet detection and timing recovery
- [ ] Improve carrier synchronization for sampled SDR waveforms
- [ ] Complete end-to-end BPSK link simulation
- [ ] Integrate both ADALM-Pluto SDRs
- [ ] Demonstrate packet transmission and telemetry recovery over the RF link
- [ ] Characterize BER, packet error rate (PER), EVM, throughput, and goodput under controlled channel conditions

## Hardware and Software

### Hardware

- 2 × Analog Devices ADALM-Pluto SDR
- RF cables, SMA adapters, and attenuators for controlled conducted testing
- External antennas for the over-the-air demonstration
- VNA access for passive RF component and antenna characterization

The intended RF operating frequency is 2.4 GHz, subject to applicable authorization, equipment configuration, and lab requirements.


### Software

- Python 3.11
- NumPy
- SciPy
- Matplotlib
- Pandas
- Pytest
- IPykernel
- Visual Studio Code

The SDR hardware interface and Pluto-specific software dependencies will be added and documented during hardware integration.

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
│       └── telemetry.py
│
├── scripts/
│   └── (simulation and hardware test scripts)
│
├── tests/
│   └── (unit and integration tests)
│
├── data/
│   └── (measurement data and saved results)
│
├── requirements.txt
├── README.md
└── .gitignore
```

### Module descriptions

| Module | Purpose |
|---|---|
| `modulation.py` | BPSK symbol mapping |
| `channel.py` | AWGN, phase, and frequency-offset channel models |
| `demodulation.py` | BPSK decisions and initial carrier synchronization |
| `metrics.py` | BER calculation |
| `packet.py` | Packet construction, CRC calculation, and packet decoding |
| `telemetry.py` | Simulated telemetry generation and binary serialization |

## Development Environment

Create and activate a Python virtual environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run scripts from the project root so that the source modules can be imported as expected.

## Project Objective

The final objective is to demonstrate a working two-node SDR telemetry link and evaluate its performance under controlled RF conditions.

The project will distinguish between simulated results and measurements obtained from the physical SDR hardware. Final conclusions will be based on recorded data, repeatable test conditions, and measured performance.

This is a ground-based communications demonstration and is not intended to represent a flight-qualified spacecraft communications system.
