from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import numpy as np

class ForceSensorPlotter:
    def __init__(self, num_channels=2, buffer_size=500):
        self.num_channels = num_channels
        self.buffer_size = buffer_size

        # Create application and window
        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsLayoutWidget(show=True, title="Force Sensor Data")
        self.win.resize(800, 600)
        self.win.setWindowTitle("Force Sensor Data Streams")

        # Create plots and buffers
        self.plots = []
        self.buffers = [np.zeros(buffer_size) for _ in range(num_channels)]
        self.curves = []

        # Set up plots
        for i in range(num_channels):
            plot = self.win.addPlot(title=f"Channel {i + 1}")
            curve = plot.plot(pen=pg.mkPen(color=(i, self.num_channels)))
            self.plots.append(plot)
            self.curves.append(curve)
            self.win.nextRow()

    def update(self, data):
        """Updates the plots with new data."""
        for i in range(self.num_channels):
            self.buffers[i][:-1] = self.buffers[i][1:]  # Shift data
            self.buffers[i][-1] = data[i]  # Add new data
            self.curves[i].setData(self.buffers[i])  # Update curve

    def run(self):
        """Starts the PyQtGraph event loop."""
        QtGui.QApplication.instance().exec_()
