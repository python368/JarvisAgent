# app/chat_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton

class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 聊天显示区
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.append("MyDesktopAI 准备就绪！输入指令：")
        layout.addWidget(self.chat_display)
        
        # 输入区
        input_layout = QVBoxLayout()
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
            self.chat_display.append(f"你: {msg}")
            self.input_field.clear()
            self.chat_display.append("AI: 开发中... (下一步接入 agent)")
            