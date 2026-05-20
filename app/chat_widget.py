# app/chat_widget.py
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from models.model_router import get_client

class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.messages: list[dict[str, str]] = []
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
        if not msg:
            return
        # ========== 气泡式对话 (用户) ==========
        self.chat_display.append(
            f"<div style='display:inline-block; padding:10px 14px; margin:6px 0; background:#2a2e3d; border-radius:12px; color:#e0e0ff; line-height:1.5; text-align:right;'>你: {msg}</div>"
        )
        self.input_field.clear()
        # Record user message
        self.messages.append({"role": "user", "content": msg})
        # Get AI response
        try:
            client = get_client()
            response = client.chat(self.messages)
        except Exception as exc:
            response = f"Error: {exc}"
        # ========== 气泡式对话 (AI) ==========
        self.chat_display.append(
            f"<div style='display:inline-block; padding:10px 14px; margin:6px 0; background:#1c1f2a; border-radius:12px; color:#e0e0ff; line-height:1.5; text-align:left;'>AI: {response}</div>"
        )
        # Record AI message
        self.messages.append({"role": "assistant", "content": response})
