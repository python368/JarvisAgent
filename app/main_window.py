from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout

from app.chat_widget import ChatWidget
from app.sidebar_widget import SidebarWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MyDesktopAI")
        self.setGeometry(200, 150, 1100, 700)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        layout = QHBoxLayout()

        # 左侧栏
        self.sidebar = SidebarWidget()

        # 主聊天区
        self.chat = ChatWidget()

        layout.addWidget(self.sidebar)
        layout.addWidget(self.chat)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)