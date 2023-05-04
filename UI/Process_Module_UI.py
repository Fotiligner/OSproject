

# 进程模块的TAB
class ProcessTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("进程模块,以后再做, 欸嘿")
        layout.addWidget(label)
        self.setLayout(layout)

