from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTableWidget, QAbstractItemView, \
    QTableWidgetItem, QPushButton, QScrollArea
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import QSize, Qt

from File_Module import FCB


class MyFigureCanvas(FigureCanvas):
    def __init__(self, parent=None, width=3.9, height=2.7, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=100)
        super(MyFigureCanvas, self).__init__(self.fig)
        self.ax = self.fig.add_subplot(111)


class FileTab(QWidget):
    def __init__(self, file_module, file_signal, parent=None):
        super().__init__(parent)
        self.file_module = file_module
        self.file_signal = file_signal
        self.file_signal.modified.connect(self.handleFileSignalEmit)
        layout = QVBoxLayout()

        self.row1_layout = QHBoxLayout()
        self.info_label = QLabel("")
        self.scrollare = QScrollArea()
        self.scrollare.setWidget(self.info_label)
        self.scrollare.setContentsMargins(0, 0, 0, 0)
        self.scrollare.setStyleSheet('QScrollArea{border:none}')
        self.scrollare.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollare.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollare.setMinimumSize(QSize(500, 300))
        self.scrollare.setMaximumSize(QSize(500, 300))
        self.row1_layout.addWidget(self.scrollare)

        self.line_figure = MyFigureCanvas()
        self.line_figure.ax.set_ylim(0, self.file_module.disk.data_blk_num)
        self.row1_layout.addWidget(self.line_figure)
        row1_col3_layout = QVBoxLayout()
        row1_col3_layout.addWidget(QLabel(u'选择文件'))
        self.file_combox = QComboBox()
        row1_col3_layout.addWidget(self.file_combox)
        row1_col3_layout.addWidget(QLabel(u'磁头寻道算法'))
        self.algo_combox = QComboBox()
        self.algo_combox.addItems(['FCFS', 'SSTF', 'SCAN', 'C-SCAN', 'LOOK', 'C-LOOK'])
        row1_col3_layout.addWidget(self.algo_combox)
        self.head_seek_display_btn = QPushButton(u'展示')
        self.head_seek_display_btn.clicked.connect(self.head_seek_display)
        row1_col3_layout.addWidget(self.head_seek_display_btn)
        self.row1_layout.addLayout(row1_col3_layout)

        self.row2_table_widget = QTableWidget()
        self.row2_table_widget.setRowCount(self.file_module.disk.track_tot_num)
        self.row2_table_widget.setColumnCount(self.file_module.disk.sector_per_track)
        self.row2_table_widget.setHorizontalHeaderLabels(
            [u'扇区' + str(i) for i in range(self.file_module.disk.sector_per_track)])
        self.row2_table_widget.setVerticalHeaderLabels(
            [u'磁道' + str(i) for i in range(self.file_module.disk.track_tot_num)])
        self.row2_table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
        self.row2_table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)  # 整行选择

        layout.addLayout(self.row1_layout)
        layout.addWidget(self.row2_table_widget)

        self.setLayout(layout)
        self.handleFileSignalEmit()

    def head_seek_display(self):
        file_name = self.file_combox.currentText()
        algo = self.algo_combox.currentText()
        file_node = self.file_module.get_fcb(file_name)
        ret_list = self.file_module.head_seek(file_node.disk_loc, algo, 371)
        y = [i[0] for i in ret_list]
        x = [i for i in range(len(ret_list))]

        self.row1_layout.removeWidget(self.scrollare)
        text = u'磁头寻道请求序列：' + str(file_node.disk_loc) + '\n'
        text += u'初始磁头位置：371    扫描方向：从小到大' + '\n'
        text += str(algo) + '调度序列：' + str(y) + '\n'
        text += u'文件内容：\n'
        text += self.file_module.read_file(file_node, algo=algo)
        self.info_label = QLabel()
        self.info_label.setText(text)
        self.scrollare = QScrollArea()
        self.scrollare.setWidget(self.info_label)
        self.scrollare.setContentsMargins(0, 0, 0, 0)
        self.scrollare.setStyleSheet('QScrollArea{border:none}')
        self.scrollare.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollare.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollare.setMinimumSize(QSize(500, 300))
        self.scrollare.setMaximumSize(QSize(500, 300))
        self.row1_layout.insertWidget(0, self.scrollare)

        self.row1_layout.removeWidget(self.line_figure)
        self.line_figure = MyFigureCanvas()
        self.line_figure.ax.set_ylim(0, self.file_module.disk.data_blk_num)
        self.line_figure.ax.set_xlim(0, len(ret_list))
        self.line_figure.ax.plot(x, y)
        self.row1_layout.insertWidget(1, self.line_figure)

    def ui_disk_display(self):
        with open(self.file_module.disk.file_path, 'a+') as f:
            size = f.tell()
            f.seek(0)
            track_no = 0
            sector_no = 0
            while f.tell() < size:
                if sector_no < self.file_module.disk.sector_per_track:
                    text = repr(f.read(self.file_module.disk.blk_size))
                    self.row2_table_widget.setItem(track_no, sector_no, QTableWidgetItem(text))
                    sector_no = sector_no + 1
                else:
                    sector_no = 0
                    track_no = track_no + 1

    def get_file_combox_item(self):
        self.file_combox.clear()
        item_list = []
        for c in self.file_module.work_dir.childs:
            if isinstance(c, FCB):
                item_list.append(c.name)
        self.file_combox.addItems(item_list)

    def handleFileSignalEmit(self):
        self.ui_disk_display()
        self.get_file_combox_item()
