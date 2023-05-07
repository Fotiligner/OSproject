from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTableWidget


class FileTab(QWidget):
    def __init__(self,file_module,file_signal,parent=None):
        super().__init__(parent)
        self.file_module = file_module
        self.file_signal = file_signal
        self.file_signal.modified.connect(self.handleFileSignalEmit)
        layout = QVBoxLayout()

        row1_layout =QHBoxLayout()
        self.file_content_label=QLabel("")
        row1_layout.addWidget(self.file_content_label)
        self.pic_label=QLabel()
        row1_layout.addWidget(self.pic_label)
        row1_col3_layout = QVBoxLayout()
        row1_col3_layout.addWidget(QLabel(u'选择文件'))
        self.file_combox=QComboBox()
        row1_col3_layout.addWidget(self.file_combox)
        row1_col3_layout.addWidget(QLabel(u'磁头寻道算法'))
        self.algo_combox=QComboBox()
        row1_col3_layout.addWidget(self.algo_combox)
        row1_layout.addLayout(row1_col3_layout)

        self.row2_table_widget = QTableWidget()
        self.row2_table_widget.setRowCount(self.file_module.disk.track_tot_num)
        self.row2_table_widget.setColumnCount(self.file_module.disk.sector_per_track)

        layout.addLayout(row1_layout)
        layout.addWidget(self.row2_table_widget)

        self.setLayout(layout)

    def handleFileSignalEmit(self):
        self.pic_label.setText("emit success")