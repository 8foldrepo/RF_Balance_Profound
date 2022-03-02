import pyqtgraph as pg
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, QtCore


class Plot(pg.PlotWidget):
    def __init__(self, parent=None):
        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")
        super().__init__(parent=parent)
        self.app = QApplication.instance()
        self.styles = {"color": "k", "font-size": "10pt"}
        self.left = 50
        self.top = 50
        self.screen_width = 1500
        self.screen_height = 750
        self.pgHoffset = 55
        self.pgWoffset = 75

        self.format_plot()

    def refresh(self, time, volts, pen="k", clear="True"):
        self.plot(time, volts, pen=pen, clear=clear)
        self.app.processEvents()
        pass

    def format_plot(self):
        color = self.palette().color(
            QPalette.Window
        )  # Get the default window background,
        self.setBackground(color)

        # plot data: x, y values
        # self.pen = pg.mkPen(color='#52988C', width=1, style=Qt.SolidLine, join=Qt.RoundJoin, cap=Qt.RoundCap)
        # self.pen = pg.mkPen(color='#52988C', width=1)
        # test the ability to add item to the view
        # bg1 = pg.BarGraphItem(x=time_ms, height=volt_mV, width=0.3, brush='r')
        # plotWidget.addItem(bg1)
        self._plot = self.plot()
        # Add Background color to white
        self.setBackground("w")
        # Add Title
        # plotWidget.setTitle("Your Title Here", color="b", size="15pt")
        # Add Axis Labels
        self.setLabel("left", "m", "Voltage (V)", **self.styles)
        self.setLabel("bottom", "Time (s)", **self.styles)
        font = QFont()
        font.setPixelSize(30)
        self.getAxis("bottom").tickFont = font
        self.getAxis("bottom").setStyle(
            tickTextOffset=20,
            tickFont=QFont("Roman times", 10),
            autoExpandTextSpace=True,
        )
        self.getAxis("bottom").setHeight(h=self.pgHoffset)
        # axBottom = plotWidget.getAxis('bottom')  # get x axis
        # xTicks = [1, 0.5]
        # axBottom.setTickSpacing(xTicks[0], xTicks[1])  # set x ticks (major and minor)
        self.getAxis("left").tickFont = font
        self.getAxis("left").setStyle(
            tickTextOffset=20,
            tickFont=QFont("Roman times", 10),
            autoExpandTextSpace=True,
        )
        self.getAxis("left").setWidth(w=self.pgWoffset)
        # axLeft = plotWidget.getAxis('left')  # get y axis
        # yTicks = [10, 5]
        # axLeft.setTickSpacing(yTicks[0], yTicks[1])  # set y ticks (major and minor)
        # Add grid
        self.showGrid(x=True, y=True, alpha=0.3)
        # # Set Range
        # plotWidget.setXRange(0, 10, padding=0.05)
        # plotWidget.setYRange(-10.0, 10.0, padding=0.05)
        # Set log mode
        # plotWidget.setLogMode(False, True)
        # Disable auto range
        # plotWidget.disableAutoRange()
        this_plot_item = self.getPlotItem()
        this_plot_item.layout.setContentsMargins(
            20, 40, 40, 20
        )  # Left, Top, Right, Bottom
