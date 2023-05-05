import sys
import random
from PyQt5.Qt import Qt
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QGraphicsView, \
    QGraphicsScene, QGraphicsItem

file_count = 50

#绘制格子的类
class Grid(QGraphicsScene):
    def __init__(self):
        super().__init__()             #调用父类（超类）的一种方法
        self.setSceneRect(0, 0, 1200, 900)
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        count = 0
        # 添加方块并设置颜色
        for i in range(0, 900, 100):
            for j in range(0, 1000, 100):
                self.add_box(j,i,pen,count)
                count += 1
    def add_box(self,i,j,pen,count):
        if count >= file_count:
            return
        color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        brush = QBrush(color, Qt.SolidPattern)
        rect = self.addRect(i, j, 80, 80, pen, brush)
        rect.setZValue(-1)
        rect.setFlag(QGraphicsItem.ItemIsSelectable)  # 设置可选中

        print(str(i) + "," + str(j))
class SceneView(QGraphicsView): # 视图创建 为grid提供场景
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 1200, 900)
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setDragMode(QGraphicsView.RubberBandDrag)

# 主页, 文件系统的tab
class MainTab(QWidget):
    def __init__(self):
        super().__init__()
        self.scene = Grid()
        self.view = SceneView(self.scene)
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.scene.selectionChanged.connect(self.on_selection_changed)

    #点击事件
    def on_selection_changed(self):
        selected_items = self.scene.selectedItems()
# 进程模块的TAB
class ProcessTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("进程模块,以后再做, 欸嘿")
        layout.addWidget(label)
        self.setLayout(layout)


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tabs = QTabWidget(self)
        # 添加标签页
        self.tab1 = MainTab()
        self.tab2 = ProcessTab()
        self.tabs.addTab(self.tab1, "首页")
        self.tabs.addTab(self.tab2, "进程模块")
        self.setCentralWidget(self.tabs)
        self.tabs.setCurrentIndex(0)# 首页
        self.setGeometry(100, 100, 1280, 960)
        self.setWindowTitle("操作系统模拟")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())