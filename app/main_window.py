# app/main_window.py
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QGraphicsDropShadowEffect
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout

from app.chat_widget import ChatWidget
from app.sidebar_widget import SidebarWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MyDesktopAI")
        self.setGeometry(200, 150, 1100, 700)

        # ========== 毛玻璃 + 圆角 + 阴影 ==========
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(0, 6)
        self.setGraphicsEffect(shadow)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("central")
        layout = QHBoxLayout(central_widget)

        # 左侧栏
        self.sidebar = SidebarWidget()
        self.sidebar.setObjectName("sidebar")

        # 主聊天区
        self.chat = ChatWidget()

        layout.addWidget(self.sidebar)
        layout.addWidget(self.chat)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
