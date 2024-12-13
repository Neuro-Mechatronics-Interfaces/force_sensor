import pyqtgraph as pg
from PyQt5.QtCore import QObject, QTimer
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
import numpy as np
import os
from collections import deque

class ForceSensorPlotter:
    def __init__(self, num_channels=2, buffer_size=500):
        """
        Initializes the PyQtGraph plotting environment.

        :param num_channels: Number of data channels (default: 2)
        :param buffer_size: Number of samples to retain in the plot (default: 500)
        """
        self.num_channels = num_channels
        self.buffer_size = buffer_size
        self.fifo_queue = deque(maxlen=buffer_size)  # FIFO queue for plotting

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
        self.sample_rate_label.setText(f"Sample Rate: 0.0 Hz")
        self.sample_rate = 0.0

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

    def update(self):
        """
        Updates the plots with new batch data.
        """
        # Update the sample rate label
        self.sample_rate_label.setText(f"Sample Rate: {self.sample_rate:.2f} Hz")

        # Update the plot data
        if self.fifo_queue:
            data = self.fifo_queue.popleft()
            for i, value in enumerate(data):
                self.data[i] = np.roll(self.data[i], -1)
                self.data[i][-1] = value
            for i, curve in enumerate(self.curves):
                curve.setData(self.data[i])

    def add_data(self, data):
        """Adds new data to the FIFO queue."""
        self.fifo_queue.append(data)

    def run(self):
        """Starts the PyQtGraph event loop."""
        self.app.exec_()
