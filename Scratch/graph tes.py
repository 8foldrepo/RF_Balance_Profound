import pyqtgraph as pg
import pyqtgraph.exporters
import numpy as np

# define the data
theTitle = "pyqtgraph plot"
y = [2,4,6,8,10,12,14,16,18,20]
x = range(0,10)

# create plot
plt = pg.plot()
print(type(plt))
plt.showGrid(x=True,y=True)

curve = plt.plot_scope(x, y, title=theTitle, pen='r')

print(type(curve))

text2 = pg.TextItem("test", anchor=(0, 0))
#text2.setParentItem(point)
plt.addItem(text2)
text2.setPos(4,10)

for i in range(100):
    curve = plt.plot_scope(x, y, title = theTitle, pen ='k', clear = True)
    plt.addItem(text2)

## Start Qt event loop.
if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1 or not hasattr(pg.QtCore, 'PYQT_VERSION'):
        pg.QtGui.QApplication.exec_()