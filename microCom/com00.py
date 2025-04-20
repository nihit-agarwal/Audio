"""
Get very basic serial line COM port check
"""

# print out com ports
import serial.tools.list_ports
ports  = serial.tools.list_ports.comports()
for port in ports:
    print(port.device) 

# Setup communication
BAUD_RATE = 3125000
ser = serial.Serial(
    port='COM3',          # Change this to your actual port (e.g., /dev/ttyUSB0)
    baudrate=BAUD_RATE,        # Baud rate
    bytesize=8,           # 8 data bits
    parity=serial.PARITY_NONE,  # No parity
    stopbits=serial.STOPBITS_ONE,  # 1 stop bits
    timeout=0             # Timeout in seconds
)

if ser is None:
    raise ValueError('Com failed')
else:
    ser.close()