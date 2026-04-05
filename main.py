import sys
from PyQt6.QtWidgets import QApplication
from app.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # ChatGPT 风格深色主题（纯 QSS，无需额外包）
    app.setStyleSheet("""
        /* 主窗口背景 */
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0f0f23, stop:1 #1a1a2e);
            color: #e0e0ff;
            font-family: 'SF Pro Display', -apple-system, sans-serif;
        }
        
        /* 聊天显示区 */
        QTextEdit {
            background-color: #1e1e2e;
            border: 1px solid #2a2a3a;
            border-radius: 12px;
            padding: 16px;
            font-size: 15px;
            line-height: 1.5;
            selection-background-color: #007aff;
        }
        
        /* 输入框 */
        QLineEdit {
            background-color: #1e1e2e;
            border: 2px solid #2a2a3a;
            border-radius: 16px;
            padding: 14px 16px;
            font-size: 15px;
            color: #ffffff;
            max-height: 48px;
        }
        QLineEdit:focus {
            border-color: #007aff;
            background-color: #232339;
            box-shadow: 0 0 0 3px rgba(0,122,255,0.1);
        }
        
        /* 发送按钮 */
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #007aff, stop:1 #0056cc);
            border: none;
            border-radius: 16px;
            padding: 14px 28px;
            color: white;
            font-weight: 600;
            font-size: 15px;
            max-height: 48px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0056cc, stop:1 #004499);
        }
        
        /* 侧边栏 */
        QWidget#sidebar {
            background-color: #161622;
            border-right: 1px solid #2a2a3a;
        }
        QPushButton#sidebar {
            background-color: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 10px;
            padding: 12px;
            margin: 6px;
            color: #e0e0ff;
            font-weight: 500;
        }
        QPushButton#sidebar:hover {
            background-color: rgba(255,255,255,0.15);
            border-color: rgba(255,255,255,0.25);
        }
        
        QLabel {
            color: #a0b2ff;
            font-size: 16px;
            font-weight: 600;
            padding: 20px 16px;
        }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()