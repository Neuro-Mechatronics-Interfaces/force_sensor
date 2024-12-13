from PyQt5.QtCore import QObject, QTimer, pyqtSignal
import serial
import struct
import time
from collections import deque

class ForceSensorConnection(QObject):
    new_data = pyqtSignal(list)  # Signal to emit new data

    def __init__(self, port, baudrate=115200, num_channels=2, batch_size=10, buffer_size=1000):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.num_channels = num_channels
        self.batch_size = batch_size
        self.serial = None
        self.sample_count = 0
        self.rate_requests = 0
        self.start_time = time.time()
        self.fifo_buffer = deque(maxlen=buffer_size)  # FIFO buffer
        self.timer = QTimer()
        self.timer.timeout.connect(self.acquire_samples)

    def connect(self):
        """Establishes a connection to the microcontroller."""
        self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
        print(f"Connected to {self.port} at {self.baudrate} baud.")

    def disconnect(self):
        """Closes the serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("Disconnected from microcontroller.")

    def acquire_samples(self):
        """Acquires samples from the microcontroller."""
        # self.serial.write('r'.encode('utf-8'))
        raw_data = self.serial.read(self.num_channels)

        if len(raw_data) == self.num_channels:
            self.sample_count += 1
            unpacked_data = struct.unpack(f"{'B' * self.num_channels}", raw_data)
            normalized_data = [float(val) / 255.0 for val in unpacked_data]
            self.fifo_buffer.append(normalized_data)
            self.new_data.emit(normalized_data)

    def start(self):
        """Starts the acquisition loop."""
        self.start_time = time.time()
        self.timer.start(100)  # Set acquisition rate (adjust as needed)

    def stop(self):
        """Stops the acquisition loop."""
        self.timer.stop()

    def get_sample_rate(self):
        """Calculates and returns the estimated sample rate (packets per second)."""
        new_time = time.time() 
        elapsed_time = new_time - self.start_time
        samples = self.sample_count
        self.rate_requests += 1
        if self.rate_requests == 100:
            self.sample_count = 0
            self.start_time = new_time
            self.rate_requests = 0
        if elapsed_time > 0:
            return samples / elapsed_time
        return 0
