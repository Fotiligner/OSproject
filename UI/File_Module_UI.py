from PyQt5.QtWidgets import QWidget, QVBoxLayout


class FileTab(QWidget):
    def __init__(self,file_module,parent=None):
        super().__init__(parent)
        self.file_module = file_module

        layout = QVBoxLayout()
        self.setLayout(layout)