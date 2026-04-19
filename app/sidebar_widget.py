# app/sidebar_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

class SidebarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # 按钮列表
        self.btn_chat = QPushButton("聊天")
        self.btn_settings = QPushButton("设置")
        self.btn_about = QPushButton("关于")

        for btn in (self.btn_chat, self.btn_settings, self.btn_about):
            btn.setObjectName("sidebar")
            layout.addWidget(btn)

        layout.addStretch(1)
