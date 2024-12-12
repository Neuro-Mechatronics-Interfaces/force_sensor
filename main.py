import sys
import argparse
from force_sensor.connection import ForceSensorConnection
from force_sensor.plotting import ForceSensorPlotter
from PyQt5.QtCore import QTimer

def parse_arguments():
    parser = argparse.ArgumentParser(description="Force Sensor Visualization Tool")
    parser.add_argument("--port", type=str, default="COM8", help="The serial port name (default: COM8).")
    parser.add_argument("--baudrate", type=int, default=115200, help="Baud rate for serial communication (default: 115200).")
    parser.add_argument("--num_channels", type=int, default=2, help="Number of channels (default: 2).")
    parser.add_argument("--buffer_size", type=int, default=500, help="Buffer size for plotting (default: 500).")
    return parser.parse_args()

def main():
    args = parse_arguments()

    print(f"Using the following configuration:")
    print(f"  Port: {args.port}")
    print(f"  Baudrate: {args.baudrate}")
    print(f"  Number of Channels: {args.num_channels}")
    print(f"  Buffer Size: {args.buffer_size}")

    connection = ForceSensorConnection(
        port=args.port, baudrate=args.baudrate, num_channels=args.num_channels
    )
    try:
        connection.connect()
    except Exception as e:
        print(f"Failed to connect to the microcontroller: {e}")
        sys.exit(1)

    plotter = ForceSensorPlotter(num_channels=args.num_channels, buffer_size=args.buffer_size)

    def update_plot():
        batch_data = connection.read_data()  # Read batched data
        if batch_data:
            sample_rate = connection.get_sample_rate()  # Get current sample rate
            plotter.update(batch_data, sample_rate)  # Update plots with batched data

    timer = QTimer()
    timer.timeout.connect(update_plot)
    timer.start(50)

    plotter.run()
    connection.disconnect()

if __name__ == "__main__":
    main()
