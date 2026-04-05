# app/sidebar_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class SidebarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("工具栏"))
        layout.addWidget(QPushButton("任务管理"))
        layout.addWidget(QPushButton("模型选择"))
        layout.addWidget(QPushButton("设置"))
        layout.addWidget(QPushButton("历史记录"))
        
        layout.addStretch()  # 占位
        self.setObjectName("sidebar")  # 让 QSS 能识别