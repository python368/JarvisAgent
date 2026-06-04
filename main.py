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

    # Modern dark theme with purple gradient accents
    app.setStyleSheet("""
        * {
            font-family: "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        QWidget {
            background: transparent;
        }

        QMainWindow {
            background: rgba(15, 15, 25, 1);
        }

        QPushButton {
            font-family: inherit;
        }

        QLineEdit, QTextEdit, QComboBox {
            font-family: inherit;
        }

        QLabel {
            font-family: inherit;
        }

        /* Custom scrollbar for all widgets */
        QScrollBar:vertical {
            background: transparent;
            width: 8px;
            border-radius: 4px;
            margin: 4px 0;
        }
        QScrollBar::handle:vertical {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 4px;
            min-height: 40px;
        }
        QScrollBar::handle:vertical:hover {
            background: rgba(255, 255, 255, 0.25);
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QScrollBar:horizontal {
            background: transparent;
            height: 8px;
            border-radius: 4px;
            margin: 0 4px;
        }
        QScrollBar::handle:horizontal {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 4px;
            min-width: 40px;
        }
        QScrollBar::handle:horizontal:hover {
            background: rgba(255, 255, 255, 0.25);
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
    """)

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
