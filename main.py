# main.py
import sys
from PyQt6.QtWidgets import QApplication
from app.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    # ========== 深色主题 + 液体玻璃效果（直接写在 main.py 中） ==========
    app.setStyleSheet("""
        QMainWindow {
            background: rgba(0, 0, 0, 0.4);
            border-radius: 15px;
        }

        QWidget#central {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
        }

        QWidget#sidebar {
            background: rgba(30, 30, 38, 0.6);
            border-right: 1px solid rgba(255,255,255,0.08);
            border-top-left-radius: 12px;
            border-bottom-left-radius: 12px;
        }

        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2a2e3d, stop:1 #1c1f2a);
            color: #e0e0ff;
            border: none;
            border-radius: 8px;
            padding: 10px 16px;
            font-size: 14px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3b3f52, stop:1 #2a2e3d);
        }

        QLineEdit {
            background: rgba(40, 44, 55, 0.6);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 8px;
            padding: 8px 12px;
            color: #e0e0ff;
            font-size: 14px;
        }
        QLineEdit:focus {
            border: 1px solid #5a9cff;
            background: rgba(45, 50, 62, 0.7);
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
            background: rgba(255,255,255,0.15);
            border-radius: 4px;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
