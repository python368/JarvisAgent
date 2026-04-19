# app/chat_widget.py
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout

class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)

        # 聊天显示区
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.append("MyDesktopAI 准备就绪！输入指令：")
        layout.addWidget(self.chat_display)

        # 输入区
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入指令...")
        self.send_btn = QPushButton("发送")

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)

        # 连接信号
        self.send_btn.clicked.connect(self.send_message)
        self.input_field.returnPressed.connect(self.send_message)

    def send_message(self):
        msg = self.input_field.text().strip()
        if msg:
            # ========== 气泡式对话 ==========
            self.chat_display.append(f"<div style='display:inline-block; padding:10px 14px; margin:6px 0; background:#2a2e3d; border-radius:12px; color:#e0e0ff; line-height:1.5; text-align:right;'>你: {msg}</div>")
            self.input_field.clear()
            self.chat_display.append("<div style='display:inline-block; padding:10px 14px; margin:6px 0; background:#1c1f2a; border-radius:12px; color:#e0e0ff; line-height:1.5; text-align:left;'>AI: 开发中... (下一步接入 agent)</div>")
