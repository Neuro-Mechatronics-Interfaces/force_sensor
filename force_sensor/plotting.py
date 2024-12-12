import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
import numpy as np
import os

class ForceSensorPlotter:
    def __init__(self, num_channels=2, buffer_size=500):
        """
        Initializes the PyQtGraph plotting environment.

        :param num_channels: Number of data channels (default: 2)
        :param buffer_size: Number of samples to retain in the plot (default: 500)
        """
        self.num_channels = num_channels
        self.buffer_size = buffer_size

        # Get the absolute path to Dumbell.png
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_dir, "Dumbell.png")

        # Create the application and main window
        self.app = QtWidgets.QApplication([])
        self.win = pg.GraphicsLayoutWidget(show=True, title="Force Sensor Data")
        self.win.resize(800, 600)
        self.win.setWindowTitle("Force Sensor Data Visualization")

        # Set the application icon
        if os.path.exists(icon_path):
            self.app.setWindowIcon(QtGui.QIcon(icon_path))

        # Add a label for the sample rate
        self.sample_rate_label = pg.LabelItem(justify="right", size="14pt")
        self.win.addItem(self.sample_rate_label, row=0, col=0, colspan=2)

        # Initialize data storage and plots
        self.data = [np.zeros(buffer_size) for _ in range(num_channels)]
        self.curves = []

        # Add plots for each channel
        for i in range(num_channels):
            plot = self.win.addPlot(row=i + 1, col=0, title=f"Channel {i + 1}")
            plot.setYRange(0, 1)  # Assuming data is rescaled with unity gain (0-1)
            curve = plot.plot(self.data[i], pen=pg.mkPen(width=2))
            self.curves.append(curve)

        # Timer for updating plots
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)  # Update rate in ms

    def update(self, data=None, sample_rate=None):
        """
        Updates the plots with new batch data.

        :param data: List of floats, where each float corresponds to one channel's value.
        :param sample_rate: The current sample rate to display.
        """
        # Update the sample rate label
        if sample_rate is not None:
            self.sample_rate_label.setText(f"Sample Rate: {sample_rate:.2f} Hz")

        # Update the plot data
        if data:
            for i, channel_data in enumerate(data):
                self.data[i] = np.roll(self.data[i], -1)  # Shift data to the left
                self.data[i][-1] = channel_data  # Add the new value

        # Update the curves
        for i, curve in enumerate(self.curves):
            curve.setData(self.data[i])

    def run(self):
        """Starts the PyQtGraph event loop."""
        self.app.exec_()
