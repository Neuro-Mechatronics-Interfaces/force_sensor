import serial
import struct

class ForceSensorConnection:
    def __init__(self, port, baudrate=115200, num_channels=2):
        self.port = port
        self.baudrate = baudrate
        self.num_channels = num_channels
        self.serial = None

    def connect(self):
        """Establishes a connection to the microcontroller."""
        self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
        print(f"Connected to {self.port} at {self.baudrate} baud.")

    def disconnect(self):
        """Closes the serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("Disconnected from microcontroller.")

    def read_data(self):
        """Reads and unpacks data from the microcontroller."""
        if not self.serial or not self.serial.is_open:
            raise ConnectionError("Serial connection is not open.")

        packet_size = self.num_channels
        raw_data = self.serial.read(packet_size)  # Read the expected number of bytes
        if len(raw_data) == packet_size:
            return struct.unpack(f"{'B' * self.num_channels}", raw_data)
        return None
