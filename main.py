import sys
import argparse
from force_sensor.connection import ForceSensorConnection
from force_sensor.plotting import ForceSensorPlotter
from PyQt5.QtCore import QTimer

def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Force Sensor Visualization Tool")
    parser.add_argument(
        "--port",
        type=str,
        default="COM8",
        help="The serial port name of the microcontroller (default: COM8).",
    )
    parser.add_argument(
        "--baudrate",
        type=int,
        default=115200,
        help="The baud rate for the serial communication (default: 115200).",
    )
    parser.add_argument(
        "--num_channels",
        type=int,
        default=2,
        help="The number of force sensor channels (default: 2).",
    )
    parser.add_argument(
        "--buffer_size",
        type=int,
        default=500,
        help="The buffer size for plotting (default: 500).",
    )
    return parser.parse_args()

def main():
    args = parse_arguments()

    # Print parsed arguments for reference
    print(f"Using the following configuration:")
    print(f"  Port: {args.port}")
    print(f"  Baudrate: {args.baudrate}")
    print(f"  Number of Channels: {args.num_channels}")
    print(f"  Buffer Size: {args.buffer_size}")

    # Initialize connection
    connection = ForceSensorConnection(
        port=args.port, baudrate=args.baudrate, num_channels=args.num_channels
    )
    try:
        connection.connect()
    except Exception as e:
        print(f"Failed to connect to the microcontroller: {e}")
        sys.exit(1)

    # Initialize plotter
    plotter = ForceSensorPlotter(
        num_channels=args.num_channels, buffer_size=args.buffer_size
    )

    # Update loop
    def update_plot():
        data = connection.read_data()
        if data:
            plotter.update(data)

    # Set up a timer for periodic updates
    timer = QTimer()
    timer.timeout.connect(update_plot)
    timer.start(10)  # Update every 10 ms

    # Run the plotter application
    plotter.run()

    # Disconnect when done
    connection.disconnect()

if __name__ == "__main__":
    main()
