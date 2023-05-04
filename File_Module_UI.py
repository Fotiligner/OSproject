import sys, os
import random
from PyQt5.Qt import Qt
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen, QIcon, QCursor, QPixmap

# 测试designer创建界面
# from main_test import Ui_MainWindow

from File_Module import File_Module, Ret_State
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QGraphicsView, \
    QGraphicsScene, QGraphicsItem, QGraphicsProxyWidget, QMenu, QAction, QInputDialog, QGraphicsPixmapItem, QTextEdit, \
    QPushButton

file_count = 20
scene_width = 1200
scene_height = 900
icon_size = 90
box_size = 100


# UI部件应该只能包含节点的文件名（目录名），为调用文件模块函数提供参数即可。UI只负责绘画。

class FileNode(QGraphicsPixmapItem):
    def __init__(self, node_name: str, node_type: str, parent=None):
        super().__init__(parent)
        self.node_type = node_type
        self.node_name = node_name
        if node_type == 'd':
            self.pix = QPixmap("image/dir.png")
        elif node_type == 'f':
            self.pix = QPixmap("image/file.png")
        self.width = icon_size
        self.height = icon_size
        self.pix = self.pix.scaled(self.width, self.height)
        self.setPixmap(self.pix)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton or event.button() == Qt.RightButton:
            super(FileNode, self).mousePressEvent(event)
            event.accept()
        else:
            event.ignore()


# 绘制格子的类
class GridScene(QGraphicsScene):
    def __init__(self):
        super().__init__()

    def mousePressEvent(self, event):
        super(GridScene, self).mousePressEvent(event)

    def add_box(self, x, y, node_name, node_type):
        fn = FileNode(node_name, node_type)
        fn.setPos(x, y)
        self.addItem(fn)
        name = self.addText(str(node_name))
        name.setX(x)
        name.setY(y + icon_size)


class MyView(QGraphicsView):  # 视图创建 为grid提供场景
    def __init__(self, scene, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.scene = scene
        self.disk_path = os.path.abspath(r".") + "\\MYDISK"
        self.file_module = File_Module(self.disk_path)
        self.layout = QVBoxLayout()

        self.setSceneRect(0, 0, scene_width, scene_height)
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setScene(self.scene)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def ui_ls(self):
        self.scene.clear()
        ls_nodes = self.file_module.ls()
        cnt = x = y = 0
        row_limit = int(scene_width / box_size)
        for n in ls_nodes:
            cnt += 1
            self.scene.add_box(x, y, n[0], n[1])
            x += box_size
            if cnt % row_limit == 0:
                x = 0
                y += box_size+15

    def mouseDoubleClickEvent(self, event):
        print("double clicked on scene")
        pos = event.pos()
        item = self.itemAt(pos)
        if isinstance(item, FileNode):
            print("find node")
            if item.node_type == 'd':
                self.file_module.cd(item.node_name)
                print(item.node_name)
            elif item.node_type == 'f':
                self.ui_vi(item.node_name)
                print(item.node_name)
            self.ui_ls()

    def ui_vi(self, file_name):
        print("vi start")
        file_node = self.file_module.get_fcb(file_name)
        text_edit = QTextEdit()
        btn_cancel = QPushButton("取消")
        btn_save_exit = QPushButton("保存并退出")
        text = self.file_module.read_file(file_node)
        text_edit.setPlainText(text)
        self.layout.addWidget(text_edit)
        self.layout.addWidget(btn_cancel)
        self.layout.addWidget(btn_save_exit)
        btn_cancel.clicked.connect(lambda: self.text_edit_cancel())
        btn_save_exit.clicked.connect(lambda: self.text_edit_save_exit(text_edit, file_node))
        self.setLayout(self.layout)

    def text_edit_cancel(self):
        self.del_layout()
        print("cancel done")

    def text_edit_save_exit(self, text_edit, file_node):
        text = text_edit.toPlainText()
        self.file_module.write_file(file_node, text)
        self.file_module.write_dir_tree()
        self.del_layout()
        print("savexit done")

    def del_layout(self):
        item_list = list(range(self.layout.count()))
        item_list.reverse()  # 倒序删除，避免影响布局顺序
        for i in item_list:
            item = self.layout.itemAt(i)
            self.layout.removeItem(item)
            if item.widget():
                item.widget().deleteLater()


# 主页, 文件系统的tab
class MainTab(QWidget):
    def __init__(self):
        super().__init__()
        self.scene = GridScene()
        self.view = MyView(self.scene)  # view搭配scene
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        self.setLayout(layout)

        # 声明在groupBox创建右键菜单
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.create_right_menu)  # 连接到菜单显示函数
        self.view.ui_ls()

    # 创建右键菜单函数
    def create_right_menu(self):
        # 菜单对象
        groupBox_menu = QMenu(self)
        selected_items = self.scene.selectedItems()
        if len(selected_items) == 0:
            action_touch = QAction(QIcon('image/touch.png'), u'新建文件', self)  # 创建菜单选项对象
            action_mkdir = QAction(QIcon('image/mkdir.png'), u'新建文件夹', self)
            action_back = QAction(QIcon('image/back.png'), u'返回上一级', self)
            groupBox_menu.addAction(action_back)
            groupBox_menu.addAction(action_touch)  # 把动作对象添加到菜单上
            groupBox_menu.addAction(action_mkdir)
            action_back.triggered.connect(self.ui_back)
            action_touch.triggered.connect(self.ui_touch)
            action_mkdir.triggered.connect(self.ui_mkdir)
        else:
            action_delete = QAction(QIcon('image/delete.png'),u'删除', self)
            groupBox_menu.addAction(action_delete)
            action_delete.triggered.connect(lambda: self.ui_delete(selected_items))
        groupBox_menu.exec_(QCursor.pos())  # 声明当鼠标在groupBox控件上右击时，在鼠标位置显示右键菜单   ,exec_,popup两个都可以，

    def ui_delete(self, selected_items):
        for i in selected_items:
            if i.node_type == 'd':
                self.view.file_module.rm(i.node_name, '-r')
            elif i.node_type == 'f':
                self.view.file_module.rm(i.node_name)
        self.view.ui_ls()

    def ui_touch(self):
        name, ok = QInputDialog.getText(self, '新建文件', '输入文件名')
        if ok and name:
            self.view.file_module.touch(name)
            self.view.ui_ls()

    def ui_mkdir(self):
        name, ok = QInputDialog.getText(self, '新建目录', '输入目录名')
        if ok and name:
            self.view.file_module.mkdir(name)
            self.view.ui_ls()

    def ui_back(self):
        self.view.file_module.cd("..")
        self.view.ui_ls()


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
        self.tabs.setCurrentIndex(0)  # 首页
        self.setGeometry(100, 100, scene_width+100, scene_height+100)
        self.resize(scene_width+100,scene_height+100)
        self.setFixedSize(scene_width+100,scene_height+100)
        self.setWindowTitle("操作系统模拟")


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = MyMainWindow()   # 主界面
#     window.show()
#     sys.exit(app.exec_())

# 新ui主函数
if __name__ == '__main__':
    app = QApplication(sys.argv)
    #window = MyMainWindow()   # 主界面
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.tab = MainTab()   # 所有原件需要在setup前初始化
    ui.tab_2 = ProcessTab()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec_())
