# app/sidebar_widget.py
"""Modern sidebar navigation for JarvisAgent."""

from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QPainter, QLinearGradient, QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect

from config.app_config import Config


class SidebarWidget(QWidget):
    """Modern sidebar with navigation buttons."""

    def __init__(self):
        super().__init__()
        self.current_page = "chat"
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: rgba(25, 25, 40, 0.95);
                border-right: 1px solid rgba(255, 255, 255, 0.06);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(8)

        # Logo area
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 20)
        logo_layout.setSpacing(4)
        
        logo_icon = QLabel("🤖")
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_icon.setStyleSheet("font-size: 40px; padding: 10px;")
        
        logo_text = QLabel("Jarvis")
        logo_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_text.setStyleSheet("""
            color: #ffffff;
            font-size: 20px;
            font-weight: 700;
            letter-spacing: 1px;
        """)
        
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_text)
        layout.addWidget(logo_container)

        # Navigation buttons
        nav_items = [
            ("chat", "💬", "对话", True),
            ("tasks", "📋", "任务", False),
            ("memory", "🧠", "记忆", False),
        ]

        for item_id, icon, text, selected in nav_items:
            btn = self._create_nav_button(icon, text, item_id, selected)
            layout.addWidget(btn)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Status indicator
        status_widget = QWidget()
        status_widget.setStyleSheet("""
            QWidget {
                background: rgba(99, 102, 241, 0.15);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        status_layout = QVBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(4)
        
        status_label = QLabel("● 就绪")
        status_label.setStyleSheet("color: #4ade80; font-size: 12px; font-weight: 500;")
        status_layout.addWidget(status_label)
        
        config = Config()
        provider = config.get("model_provider", "OpenAI")
        model_label = QLabel(f"模型: {provider}")
        model_label.setStyleSheet("color: rgba(255, 255, 255, 0.5); font-size: 11px;")
        status_layout.addWidget(model_label)
        
        layout.addWidget(status_widget)

        # Settings button at bottom
        layout.addSpacing(12)
        
        self.btn_settings = QPushButton("⚙️  设置")
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.05);
                color: rgba(255, 255, 255, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 14px;
                font-size: 14px;
                text-align: left;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
            }
        """)
        layout.addWidget(self.btn_settings)

    def _create_nav_button(self, icon: str, text: str, item_id: str, selected: bool = False) -> QPushButton:
        """Create a styled navigation button."""
        btn = QPushButton(f"{icon}  {text}")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setObjectName(item_id)
        
        if selected:
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(99, 102, 241, 0.3), stop:1 rgba(139, 92, 246, 0.2));
                    color: #ffffff;
                    border: 1px solid rgba(99, 102, 241, 0.4);
                    border-radius: 12px;
                    padding: 14px 16px;
                    font-size: 14px;
                    text-align: left;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(99, 102, 241, 0.4), stop:1 rgba(139, 92, 246, 0.3));
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: rgba(255, 255, 255, 0.6);
                    border: none;
                    border-radius: 12px;
                    padding: 14px 16px;
                    font-size: 14px;
                    text-align: left;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.05);
                    color: rgba(255, 255, 255, 0.9);
                }
            """)
        
        return btn
