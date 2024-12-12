import sys
from force_sensor.connection import ForceSensorConnection
from force_sensor.plotting import ForceSensorPlotter
from PyQt5.QtCore import QTimer

def main():
    port = "COM8"  # Replace with your serial port
    num_channels = 2  # Default number of channels
    buffer_size = 500  # Default buffer size for plotting

    # Initialize connection
    connection = ForceSensorConnection(port, num_channels=num_channels)
    try:
        connection.connect()
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

    # Initialize plotter
    plotter = ForceSensorPlotter(num_channels=num_channels, buffer_size=buffer_size)

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
