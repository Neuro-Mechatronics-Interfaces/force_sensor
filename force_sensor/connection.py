import serial
import struct
import time

class ForceSensorConnection:
    def __init__(self, port, baudrate=115200, num_channels=2, batch_size=10):
        self.port = port
        self.baudrate = baudrate
        self.num_channels = num_channels
        self.batch_size = batch_size
        self.serial = None
        self.sample_count = 0
        self.start_time = time.time()

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
        """
        Reads and unpacks a batch of raw unsigned long data from the microcontroller.
        Each channel transmits BUFFER_SIZE unsigned long values.
        """
        raw_data = self.serial.read(self.num_channels)

        if len(raw_data) == self.num_channels:
            self.sample_count += 1
            # Unpack all bytes as unsigned integers
            unpacked_data = struct.unpack(f"{'B' * self.num_channels}", raw_data)
            # Split data into per-channel lists
            channel_data = [
                float(unpacked_data[0]) / 255.0,  # Channel 1 (w1 values)
                float(unpacked_data[1]) / 255.0  # Channel 2 (w2 values)
            ]
            return channel_data  # Returns a list of lists, one per channel
        return None

    def get_sample_rate(self):
        """Calculates and returns the estimated sample rate (packets per second)."""
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            return self.sample_count / elapsed_time
        return 0
