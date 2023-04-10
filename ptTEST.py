import sys
import random
from PyQt5.Qt import Qt
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QGraphicsView, \
    QGraphicsScene, QGraphicsItem


class Grid(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 1200, 900)
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        count=0
        # 添加方块并设置颜色
        for i in range(0, 1200, 100):
            for j in range(0, 900, 100):
                color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                brush = QBrush(color, Qt.SolidPattern)
                rect = self.addRect(j, i, 80, 80, pen, brush)
                rect.setZValue(-1)
                rect.setFlag(QGraphicsItem.ItemIsSelectable)  # 设置可选中
                count+=1
                if count >= 10:
                    break
            else:
                continue



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
    # 连接方块的点击事件
        self.scene.selectionChanged.connect(self.on_selection_changed)

    def on_selection_changed(self):
        selected_items = self.scene.selectedItems()
        print(f"Selected items: {[item.data(0) for item in selected_items]}")

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