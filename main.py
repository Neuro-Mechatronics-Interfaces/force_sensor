from PyQt5.QtCore import QTimer
from force_sensor.connection import ForceSensorConnection
from force_sensor.plotting import ForceSensorPlotter
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Force Sensor Visualization Tool")
    parser.add_argument("--port", type=str, default="COM8", help="The serial port name (default: COM8).")
    parser.add_argument("--baudrate", type=int, default=115200, help="Baud rate for serial communication (default: 115200).")
    parser.add_argument("--num_channels", type=int, default=2, help="Number of channels (default: 2).")
    parser.add_argument("--buffer_size", type=int, default=500, help="Buffer size for plotting (default: 500).")
    return parser.parse_args()

def main():
    args = parse_arguments()

    connection = ForceSensorConnection(port=args.port, baudrate=args.baudrate, num_channels=args.num_channels)
    plotter = ForceSensorPlotter(num_channels=args.num_channels, buffer_size=args.buffer_size)

    def transfer_data():
        """Transfers data from the connection buffer to the plotter."""
        while connection.fifo_buffer:
            data = connection.fifo_buffer.popleft()
            plotter.add_data(data)
        plotter.sample_rate = connection.get_sample_rate()

    try:
        connection.connect()
        connection.start()

        # Timer for transferring data
        transfer_timer = QTimer()
        transfer_timer.timeout.connect(transfer_data)
        transfer_timer.start(50)

        plotter.run()
    finally:
        connection.stop()
        connection.disconnect()

if __name__ == "__main__":
    main()
