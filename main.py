# main.py
"""Main entry point for JarvisAgent application."""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTranslator, QLocale
from app.main_window import MainWindow


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    
    # Configure application metadata
    app.setApplicationName("JarvisAgent")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("JarvisAgent")
    app.setOrganizationDomain("jarvisagent.app")
    
    # Set high DPI scaling
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Global dark stylesheet
    app.setStyleSheet("""
        * {
            font-family: "SF Pro Display", "Helvetica Neue", -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        QWidget {
            background: transparent;
        }
        
        QMainWindow {
            background: rgba(20, 20, 28, 0.95);
        }
        
        QWidget#central {
            background: rgba(30, 30, 40, 0.6);
            border-radius: 15px;
        }
        
        QWidget#sidebar {
            background: rgba(35, 35, 48, 0.8);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3b4252, stop:1 #2e3440);
            color: #e0e0ff;
            border: none;
            border-radius: 8px;
            padding: 10px 16px;
            font-size: 14px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #434c5e, stop:1 #3b4252);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2e3440, stop:1 #282c34);
        }
        
        QLineEdit, QComboBox {
            background: rgba(40, 44, 55, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 8px;
            padding: 10px 14px;
            color: #e0e0ff;
            font-size: 14px;
        }
        QLineEdit:focus, QComboBox:focus {
            border: 1px solid #5a9cff;
            background: rgba(45, 50, 62, 0.7);
        }
        QLineEdit:disabled, QComboBox:disabled {
            background: rgba(30, 30, 40, 0.4);
            color: rgba(255, 255, 255, 0.4);
        }
        QComboBox::drop-down {
            border: none;
            padding-right: 8px;
        }
        QComboBox QAbstractItemView {
            background: rgba(40, 44, 55, 0.98);
            border: 1px solid rgba(255, 255, 255, 0.1);
            selection-background-color: rgba(90, 156, 255, 0.3);
        }
        
        QTextEdit {
            background: transparent;
            border: none;
            font-size: 14px;
            color: #e0e0ff;
        }
        
        QScrollBar:vertical {
            background: transparent;
            width: 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 4px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover {
            background: rgba(255, 255, 255, 0.25);
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QLabel {
            color: #c0c0d0;
            background: transparent;
        }
    """)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
