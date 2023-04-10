import sys

from PyQt5 import Qt
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QGraphicsView, \
    QGraphicsScene


class Grid(QGraphicsScene):
    def __init__(self):
        super().__init__()

        self.setSceneRect(0, 0, 1200, 900)
        self.setItemIndexMethod(self.NoIndex)
        # 添加网格线
        pen = QColor("#cccccc")
        for x in range(0, 1281, 100):
            self.addLine(x, 0, x, 600, pen)

        for y in range(0, 601, 100):
            self.addLine(0, y, 1200, y, pen)


class SceneView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 1200, 900)
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setDragMode(QGraphicsView.RubberBandDrag)


class MainTab(QWidget):
    def __init__(self):
        super().__init__()

        # 创建 QGraphicsScene 和 QGraphicsView
        self.scene = Grid()
        self.view = SceneView(self.scene)

        # 将 QGraphicsView 添加到布局中
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        self.setLayout(layout)


class ProcessTab(QWidget):
    def __init__(self):
        super().__init__()

        # 添加元素和布局
        layout = QVBoxLayout()
        label = QLabel("进程模块")
        layout.addWidget(label)

        self.setLayout(layout)


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建 QTabWidget 控件
        self.tabs = QTabWidget(self)

        # 添加标签页到 QTabWidget 中
        self.tab1 = MainTab()
        self.tab2 = ProcessTab()

        self.tabs.addTab(self.tab1, "首页")
        self.tabs.addTab(self.tab2, "进程模块")


        # 将 QTabWidget 添加到主窗口中
        self.setCentralWidget(self.tabs)

        # 设置当前显示的标签页
        self.tabs.setCurrentIndex(0)


        self.setGeometry(100, 100, 1280, 960)
        self.setWindowTitle("操作系统模拟")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())