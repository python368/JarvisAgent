# app/main_window.py
"""Main window for JarvisAgent application."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PyQt6 import QtCore

from app.chat_widget import ChatWidget
from app.sidebar_widget import SidebarWidget
from app.settings_window import SettingsWindow


class MainWindow(QMainWindow):
    """Main application window with chat interface."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Jarvis Agent")
        self.setGeometry(200, 150, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Frameless window with shadow
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)
        
        self.init_ui()
    
    def init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("central")
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title bar area
        title_bar = self._create_title_bar()
        layout.addWidget(title_bar, 0, Qt.AlignmentFlag(0))
        
        # Sidebar
        self.sidebar = SidebarWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)
        self.sidebar.btn_settings.clicked.connect(self.open_settings)
        layout.addWidget(self.sidebar, 0)
        
        # Main chat area
        self.chat = ChatWidget()
        layout.addWidget(self.chat, 1)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    def _create_title_bar(self):
        """Create custom title bar with drag region."""
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("""
            QWidget {
                background: rgba(25, 25, 35, 0.95);
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
            }
        """)
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(15, 0, 10, 0)
        
        # App title
        title = QLabel("🤖 Jarvis Agent")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #e0e0ff;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Window controls
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        
        for btn_type, icon in [("minimize", "─"), ("maximize", "□"), ("close", "✕")]:
            btn = QLabel(icon)
            btn.setFixedSize(20, 20)
            btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn.setStyleSheet(f"""
                QLabel {{
                    color: #888;
                    font-size: 12px;
                    border-radius: 4px;
                }}
                QLabel:hover {{
                    background: rgba(255, 255, 255, 0.1);
                    color: #fff;
                }}
            """)
            if btn_type == "close":
                btn.setStyleSheet("""
                    QLabel {
                        color: #888;
                        font-size: 12px;
                        border-radius: 4px;
                    }
                    QLabel:hover {
                        background: rgba(255, 60, 60, 0.8);
                        color: #fff;
                    }
                """)
                btn.mousePressEvent = lambda e: self.close()
            elif btn_type == "minimize":
                btn.mousePressEvent = lambda e: self.showMinimized()
            controls_layout.addWidget(btn)
        
        layout.addWidget(controls)
        
        # Enable dragging
        title_bar.mouseMoveEvent = self._title_bar_mouse_move
        title_bar.mousePressEvent = self._title_bar_mouse_press
        
        return title_bar
    
    def _title_bar_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
    
    def _title_bar_mouse_move(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self._drag_pos)
    
    def open_settings(self):
        """Open the settings dialog."""
        settings = SettingsWindow(self)
        settings.exec()
