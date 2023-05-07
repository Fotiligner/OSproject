import sys, os
from PyQt5.Qt import Qt
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QRegExp, QObject, pyqtSignal
from PyQt5.QtGui import QPainter, QIcon, QCursor, QPixmap, QIntValidator, QRegExpValidator

# 测试designer创建界面
# from main_test import Ui_MainWindow

from File_Module import File_Module
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QGraphicsView, \
    QGraphicsScene, QGraphicsItem, QMenu, QAction, QInputDialog, QGraphicsPixmapItem, QTextEdit, \
    QPushButton, QMessageBox, QLabel, QDialog, QGridLayout, QLineEdit, QDialogButtonBox, QRadioButton

# from UI.main_test import Ui_MainWindow

file_count = 20
scene_width = 1200
scene_height = 900
icon_size = 90
box_size = 100


# UI部件应该只能包含节点的文件名（目录名），为调用文件模块函数提供参数即可。UI只负责绘画。

class EmittingStr(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text, ui):
        self.textWritten.emit(str(text))
        loop = QEventLoop()
        QTimer.singleShot(100, loop.quit)
        loop.exec_()

    def outputWritten(self, text):
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textBrowser.setTextCursor(cursor)
        self.textBrowser.ensureCursorVisible()


class FileNode(QGraphicsPixmapItem):
    def __init__(self, node_name: str, node_type: str, parent=None):
        super().__init__(parent)
        self.node_type = node_type
        self.node_name = node_name
        if node_type == 'd':
            self.pix = QPixmap("./UI/image/dir.png")
        elif node_type == 'f':
            self.pix = QPixmap("./UI/image/file.png")
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


def del_layout(layout):
    item_list = list(range(layout.count()))
    item_list.reverse()  # 倒序删除，避免影响布局顺序
    for i in item_list:
        item = layout.itemAt(i)
        layout.removeItem(item)
        if item.widget():
            item.widget().deleteLater()


class MyView(QGraphicsView):  # 视图创建 为grid提供场景
    def __init__(self, scene, file_module, file_signal, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.scene = scene
        self.file_module = file_module
        self.file_signal = file_signal
        self.layout = QVBoxLayout()

        self.init_ui()

    def init_ui(self):
        self.setSceneRect(0, 0, scene_width, scene_height)
        self.setScene(self.scene)
        # 设置渲染属性
        self.setRenderHints(QPainter.Antialiasing |  # 抗锯齿
                            QPainter.HighQualityAntialiasing |  # 高品质抗锯齿
                            QPainter.TextAntialiasing |  # 文字抗锯齿
                            QPainter.SmoothPixmapTransform |  # 使图元变换更加平滑
                            QPainter.LosslessImageRendering)  # 不失真的图片渲染
        # 视窗更新模式
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        # 设置水平和竖直方向的滚动条不显示
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

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
                y += box_size + 15

    def mouseDoubleClickEvent(self, event):
        pos = event.pos()
        item = self.itemAt(pos)
        if isinstance(item, FileNode):
            if item.node_type == 'd':
                self.file_module.cd(item.node_name)
                self.file_signal.modified.emit()
            elif item.node_type == 'f':
                self.ui_vi(item.node_name)

    def ui_vi(self, file_name):
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
        del_layout(self.layout)

    def text_edit_save_exit(self, text_edit, file_node):
        text = text_edit.toPlainText()
        self.file_module.write_file(file_node, text)
        self.file_module.write_dir_tree()
        del_layout(self.layout)
        self.file_signal.modified.emit()


# 主页, 文件系统的tab
class MainTab(QWidget):
    def __init__(self, file_module, process_module, file_signal):
        super().__init__()
        self.file_signal = file_signal
        self.scene = GridScene()
        self.file_module = file_module
        self.process_module = process_module
        self.view = MyView(self.scene, self.file_module, self.file_signal)  # view搭配scene
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.file_signal.modified.connect(self.handleFileSignalEmit)

        # 声明在groupBox创建右键菜单
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.create_right_menu)  # 连接到菜单显示函数

        self.view.ui_ls()

        # 临时创建，为了让主界面可以调用
        self.action_cmd = QAction(QIcon('./UI/image/cmd.png'), u'控制台', self)

    def handleFileSignalEmit(self):
        self.view.ui_ls()

    # 创建右键菜单函数
    def create_right_menu(self):
        # 菜单对象
        groupBox_menu = QMenu(self)
        selected_items = self.scene.selectedItems()
        if len(selected_items) == 0:
            action_touch = QAction(QIcon('./UI/image/touch.png'), u'新建文件', self)  # 创建菜单选项对象
            action_mkdir = QAction(QIcon('./UI/image/mkdir.png'), u'新建文件夹', self)
            action_back = QAction(QIcon('./UI/image/back.png'), u'返回上一级', self)

            groupBox_menu.addAction(action_back)
            groupBox_menu.addAction(action_touch)  # 把动作对象添加到菜单上
            groupBox_menu.addAction(action_mkdir)
            groupBox_menu.addAction(self.action_cmd)

            action_back.triggered.connect(self.ui_back)
            action_touch.triggered.connect(self.ui_touch)
            action_mkdir.triggered.connect(self.ui_mkdir)
        else:
            action_delete = QAction(QIcon('./UI/image/delete.png'), u'删除', self)
            groupBox_menu.addAction(action_delete)
            action_delete.triggered.connect(lambda: self.ui_delete(selected_items))

            if len(selected_items) == 1 and selected_items[0].node_type == 'f':
                action_info = QAction(QIcon('./UI/image/info.png'), u'详情', self)
                groupBox_menu.addAction(action_info)
                action_info.triggered.connect(lambda: self.ui_info(selected_items[0].node_name))

            # 若是可执行文件(exe结尾)则显示运行选项：
            show_run = True
            for i in selected_items:
                if i.node_type != 'f':
                    show_run = False
                    break

            if show_run:
                action_run = QAction(QIcon('./UI/image/run.png'), u'运行', self)
                groupBox_menu.addAction(action_run)
                action_run.triggered.connect(lambda: self.ui_run(selected_items))
            # else:   # 显示报错，有不可执行的文件
            #     # 后两项分别为按钮(以|隔开，共有7种按钮类型，见示例后)、默认按钮(省略则默认为第一个按钮)
            #     reply = QMessageBox.information(self, "Error", "Non-executable files included", QMessageBox.OK,
            #                                     QMessageBox.OK)

        groupBox_menu.exec_(QCursor.pos())  # 声明当鼠标在groupBox控件上右击时，在鼠标位置显示右键菜单   ,exec_,popup两个都可以，

    class _InfoWidget(QWidget):
        def __init__(self, fcb):
            super().__init__()
            self.setWindowTitle("文件详情")
            self.layout = QVBoxLayout(self)
            file_name = QLabel("文件名称:" + fcb.name)
            file_size = QLabel("文件大小:" + str(fcb.size))
            file_blk_num = QLabel("所占磁盘块数:" + str(fcb.blk_num))
            file_disk_loc = QLabel("磁盘块地址:" + str(fcb.disk_loc))
            file_auth = QLabel("文件权限:" + fcb.auth)
            self.layout.addWidget(file_name)
            self.layout.addWidget(file_size)
            self.layout.addWidget(file_auth)
            self.layout.addWidget(file_blk_num)
            self.layout.addWidget(file_disk_loc)
            self.layout.setContentsMargins(100, 30, 200, 30)
            self.layout.setSpacing(50)  # 设置间距
            self.setLayout(self.layout)

    def ui_info(self, file_name):
        fcb = self.view.file_module.get_fcb(file_name)
        self.info_win = self._InfoWidget(fcb=fcb)
        self.info_win.show()

    def ui_delete(self, selected_items):
        for i in selected_items:
            if i.node_type == 'd':
                self.view.file_module.rm(i.node_name, '-r')
            elif i.node_type == 'f':
                self.view.file_module.rm(i.node_name)
        self.file_signal.modified.emit()

    def ui_run(self, selected_items):
        is_executable = True
        for i in selected_items:
            print(i.node_name)
            if len(i.node_name) < 4 or (len(i.node_name) >= 4 and not(i.node_name[-4:] == ".exe" or i.node_name[-2:] == ".e")):
                is_executable = False
                break

        print(is_executable)

        if not is_executable:
            reply = QMessageBox.information(self, "Error", "Non-executable files included",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        else:
            for i in selected_items:
                self.process_module.create_process(i.node_name, 1)

    class _TouchDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)

            self.select_btn_ran = None
            self.select_btn_def = None
            self.file_size_edit = None
            self.setWindowTitle(u'新建文件')

            self.grid = QGridLayout()
            # self.grid.setContentsMargins(100, 30, 200, 30)
            # self.grid.setSpacing(50)  # 设置间距
            self.grid.addWidget(QLabel(u'文件名'), 0, 0)
            self.file_name_edit = QLineEdit(parent=self)
            reg = QRegExp("[^ \\/:*?\"<>|]*")  # 设置文本不允许出现的字符内容
            pValidator = QRegExpValidator(self)  # 自定义文本验证器
            pValidator.setRegExp(reg)  # 设置属性
            self.file_name_edit.setValidator(pValidator)
            self.grid.addWidget(self.file_name_edit, 0, 1)

            btn_box = QDialogButtonBox(Qt.Horizontal, self)
            btn_box_plus = QPushButton(u'高级', self)
            btn_box.addButton(btn_box_plus, QDialogButtonBox.ActionRole)
            btn_box_ok = QPushButton(u'确定', self)
            btn_box.addButton(btn_box_ok, QDialogButtonBox.AcceptRole)
            btn_box_cancel = QPushButton(u'取消', self)
            btn_box.addButton(btn_box_cancel, QDialogButtonBox.RejectRole)
            self.grid.addWidget(btn_box, 1, 0, 1, 2)

            btn_box.accepted.connect(self.accept)
            btn_box.rejected.connect(self.reject)
            btn_box_plus.clicked.connect(self.ui_plus)

            self.setLayout(self.grid)

        def ui_plus(self):
            del_layout(self.grid)

            # self.grid.setContentsMargins(100, 30, 200, 30)
            # self.grid.setSpacing(50)  # 设置间距

            self.grid.addWidget(QLabel(u'文件名'), 0, 0, 1, 1)
            self.file_name_edit = QLineEdit(parent=self)
            reg = QRegExp("[^ \\/:*?\"<>|]*")
            pValidator = QRegExpValidator(self)
            pValidator.setRegExp(reg)
            self.file_name_edit.setValidator(pValidator)
            self.grid.addWidget(self.file_name_edit, 0, 1, 1, 2)

            self.grid.addWidget(QLabel(u'文件大小'), 1, 0, 1, 1)
            self.file_size_edit = QLineEdit(parent=self)
            reg = QRegExp("[0-9]*")
            pValidator = QRegExpValidator(self)  # 自定义文本验证器
            pValidator.setRegExp(reg)  # 设置属性
            self.file_size_edit.setValidator(pValidator)
            self.grid.addWidget(self.file_size_edit, 1, 1, 1, 2)

            self.grid.addWidget(QLabel(u'分配方式'), 2, 0)
            self.select_btn_def = QRadioButton(u'默认', parent=self)
            self.grid.addWidget(self.select_btn_def, 2, 1, 1, 1)
            self.select_btn_ran = QRadioButton(u'随机', parent=self)
            self.grid.addWidget(self.select_btn_ran, 2, 2, 1, 1)
            self.select_btn_def.setChecked(True)

            btn_box = QDialogButtonBox(Qt.Horizontal, self)
            btn_box_ok = QPushButton(u'确定', self)
            btn_box.addButton(btn_box_ok, QDialogButtonBox.AcceptRole)
            btn_box_cancel = QPushButton(u'取消', self)
            btn_box.addButton(btn_box_cancel, QDialogButtonBox.RejectRole)
            self.grid.addWidget(btn_box, 3, 0, 1, 3)

            btn_box.accepted.connect(self.accept)
            btn_box.rejected.connect(self.reject)

    def ui_touch(self):
        touch_dialog = self._TouchDialog()
        if touch_dialog.exec_():
            file_name = touch_dialog.file_name_edit.text()
            if touch_dialog.file_size_edit:
                file_size = int(touch_dialog.file_size_edit.text())
                alloc_method = "default"
                if touch_dialog.select_btn_ran.isChecked():
                    alloc_method = "random"
                print("file_size:%d alloc_method:%s" % (file_size, alloc_method))
                self.view.file_module.touch(name=file_name, size=file_size, alloc_method=alloc_method)
            else:
                self.view.file_module.touch(name=file_name)
            self.file_signal.modified.emit()

    def ui_mkdir(self):
        name, ok = QInputDialog.getText(self, '新建目录', '输入目录名')
        if ok and name:
            self.view.file_module.mkdir(name)
            self.file_signal.modified.emit()

    def ui_back(self):
        self.view.file_module.cd("..")
        self.file_signal.modified.emit()


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tabs = QTabWidget(self)
        # 添加标签页
        self.tab1 = MainTab()
        self.tab2 = Process_Module_UI.ProcessTab()
        self.tabs.addTab(self.tab1, "首页")
        self.tabs.addTab(self.tab2, "进程模块")
        self.tabs.addTab(self.tab4, "进程模块")
        self.setCentralWidget(self.tabs)
        self.tabs.setCurrentIndex(0)  # 首页
        self.setGeometry(100, 100, scene_width + 100, scene_height + 100)
        self.resize(scene_width + 100, scene_height + 100)
        self.setFixedSize(scene_width + 100, scene_height + 100)
        self.setWindowTitle("操作系统模拟")

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = MyMainWindow()   # 主界面
#     window.show()
#     sys.exit(app.exec_())
