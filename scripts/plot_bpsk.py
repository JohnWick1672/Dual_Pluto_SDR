import sys
sys.path.insert(0,'src')

import numpy as np
import matplotlib.pyplot as plt
from sdr_project.modulation import bpsk_modulation



# Generate test bits
bits = np.array([0, 1, 1, 0, 1, 0])

# Modulate
symbols = bpsk_modulation(bits)

# Extract I and Q
I = np.real(symbols)
Q = np.imag(symbols)

# Plot constellation
plt.figure(figsize=(8, 6))
plt.scatter(I, Q, s=120, marker='o', label='BPSK symbols')

# Label the symbols
plt.annotate('Bit 0', (1, 0), xytext=(1, 0.12), ha='center')
plt.annotate('Bit 1', (-1, 0), xytext=(-1, 0.12), ha='center')

# Formatting
plt.axhline(0, color='black', linewidth=0.8)
plt.axvline(0, color='black', linewidth=0.8)
plt.xlim(-1.5, 1.5)
plt.ylim(-0.5, 0.5)
plt.xticks([-1, 0, 1])
plt.yticks([-0.5, 0, 0.5])
plt.xlabel('In-Phase (I)')
plt.ylabel('Quadrature (Q)')
plt.title('BPSK Constellation Diagram')
plt.grid(True, alpha=0.4)
plt.gca().set_aspect('equal', adjustable='box')
plt.legend()
plt.tight_layout()
plt.show()
