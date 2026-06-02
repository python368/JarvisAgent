# app/sidebar_widget.py
"""Sidebar widget for navigation and quick actions."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt


class SidebarWidget(QWidget):
    """Sidebar navigation widget."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(10)
        
        # Logo/Title
        logo_label = QLabel("🤖")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("font-size: 32px;")
        layout.addWidget(logo_label)
        
        title = QLabel("Jarvis")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #e0e0ff;")
        layout.addWidget(title)
        
        subtitle = QLabel("AI 助手")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 12px; color: #888; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Navigation buttons
        self.btn_chat = self._create_nav_button("💬", "对话")
        self.btn_tasks = self._create_nav_button("📋", "任务")
        self.btn_history = self._create_nav_button("📜", "历史")
        self.btn_settings = self._create_nav_button("⚙️", "设置")
        
        for btn in (self.btn_chat, self.btn_tasks, self.btn_history, self.btn_settings):
            layout.addWidget(btn)
        
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Status indicator
        status_label = QLabel("● 在线")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet("color: #4caf50; font-size: 12px;")
        layout.addWidget(status_label)
    
    def _create_nav_button(self, icon: str, text: str) -> QPushButton:
        """Create a styled navigation button."""
        btn = QPushButton(f"{icon}  {text}")
        btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                color: #a0a0b0;
                font-size: 14px;
                text-align: left;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.05);
                color: #e0e0ff;
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.08);
            }
        """)
        return btn
