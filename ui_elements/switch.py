from PyQt5.QtCore import (
    QObject,
    QSize,
    QPointF,
    pyqtProperty,
    pyqtSlot,
    Qt,
)
from PyQt5.QtGui import QPainter, QPalette, QLinearGradient, QGradient, QColor
from PyQt5.QtWidgets import QAbstractButton, QApplication


class SwitchPrivate(QObject):
    def __init__(self, q, parent=None):
        self.checked = False
        QObject.__init__(self, parent=parent)
        self.mPointer = q
        self.mPosition = 0.0
        self.mGradient = QLinearGradient()
        self.mGradient.setSpread(QGradient.PadSpread)

        # Animation, try to get this working later if time permits

        # self.animation = QPropertyAnimation(self)
        # self.animation.setTargetObject(self)
        # self.animation.setPropertyName(b'position')
        # self.animation.setStartValue(0.0)
        # self.animation.setEndValue(1.0)
        # self.animation.setDuration(200)
        # self.animation.setEasingCurve(QEasingCurve.InOutExpo)

        # self.animation.finished.connect(self.mPointer.update)

    @pyqtProperty(float)
    def position(self):
        return self.mPosition

    @position.setter
    def position(self, value):
        self.mPosition = value
        self.mPointer.update()

    def draw(self, painter):
        r = self.mPointer.rect()
        margin = r.height() / 10
        shadow = self.mPointer.palette().color(QPalette.Dark)
        light = self.mPointer.palette().color(QPalette.Light)
        button = self.mPointer.palette().color(QPalette.Button)
        painter.setPen(Qt.NoPen)

        self.mGradient.setColorAt(0, shadow.darker(130))
        self.mGradient.setColorAt(1, light.darker(130))
        self.mGradient.setStart(0, r.height())
        self.mGradient.setFinalStop(0, 0)
        painter.setBrush(self.mGradient)
        painter.drawRoundedRect(r, r.height() / 2, r.height() / 2)

        self.mGradient.setColorAt(0, shadow.darker(140))
        self.mGradient.setColorAt(1, light.darker(160))
        self.mGradient.setStart(0, 0)
        self.mGradient.setFinalStop(0, r.height())
        painter.setBrush(self.mGradient)

        if self.checked:
            painter.setBrush(QColor("#30C030"))

        painter.drawRoundedRect(
            r.adjusted(int(margin), int(margin), int(-margin), int(-margin)), int(r.height() / 2), int(r.height() / 2)
        )

        self.mGradient.setColorAt(0, button.darker(130))
        self.mGradient.setColorAt(1, button)

        painter.setBrush(self.mGradient)

        x = r.height() / 2.0 + self.mPosition * (r.width() - r.height())
        painter.drawEllipse(
            QPointF(x, r.height() / 2), r.height() / 2 - margin, r.height() / 2 - margin
        )

    @pyqtSlot(bool, name="animate")
    def animate(self, checked):
        self.checked = checked
        if checked:
            self.mPosition = 1.0
            self.mPointer.update()
        else:
            self.mPosition = 0
            self.mPointer.update()

        # self.animation.setDirection(QPropertyAnimation.Forward if checked else QPropertyAnimation.Backward)
        # self.animation.start()


class Switch(QAbstractButton):
    def __init__(self, parent=None):
        QAbstractButton.__init__(self, parent=parent)
        self.dPtr = SwitchPrivate(self)
        self.setCheckable(True)
        # self.clicked.connect(self.dPtr.animate)

    def setChecked(self, checked: bool):
        super().setChecked(checked)
        self.dPtr.animate(checked)

    def sizeHint(self):
        return QSize(84, 42)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.dPtr.draw(painter)

    def resizeEvent(self, event):
        self.update()


# class Switch(Toggle) :
#    def __init__(self, form):
#        super().__init__(checked_color="#30C030")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = Switch()
    w.show()
    sys.exit(app.exec_())
