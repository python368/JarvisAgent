# app/chat_widget.py
"""Modern chat widget for JarvisAgent application."""

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QTextCursor, QFont, QPainter, QLinearGradient, QPalette, QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt6 import QtCore

from models.model_router import get_client


class StreamingWorker(QObject):
    """Worker thread for streaming AI responses."""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    chunk = pyqtSignal(str)
    
    def __init__(self, client, messages):
        super().__init__()
        self.client = client
        self.messages = messages
    
    def run(self):
        try:
            full_response = ""
            import asyncio
            
            async def stream_async():
                nonlocal full_response
                try:
                    async for chunk in self.client.chat_stream(self.messages):
                        full_response += chunk
                        self.chunk.emit(chunk)
                except Exception as e:
                    self.error.emit(str(e))
                    return
                self.finished.emit(full_response)
            
            asyncio.run(stream_async())
        except Exception as e:
            self.error.emit(str(e))


class ChatWidget(QWidget):
    """Modern chat interface with elegant design."""
    
    def __init__(self):
        super().__init__()
        self.messages = []
        self.streaming = False
        self.current_response = ""
        self.worker = None
        self.thread = None
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 24)
        layout.setSpacing(16)

        # Welcome header with animation effect
        welcome_widget = QWidget()
        welcome_widget.setFixedHeight(120)
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setContentsMargins(0, 20, 0, 0)
        welcome_layout.setSpacing(8)
        
        welcome_icon = QLabel("✨")
        welcome_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_icon.setStyleSheet("font-size: 36px;")
        
        welcome_title = QLabel("Jarvis AI 助手")
        welcome_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_title.setStyleSheet("""
            color: #ffffff;
            font-size: 24px;
            font-weight: 600;
            letter-spacing: 0.5px;
        """)
        
        welcome_subtitle = QLabel("您的智能计算机控制助手")
        welcome_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_subtitle.setStyleSheet("""
            color: rgba(255, 255, 255, 0.5);
            font-size: 14px;
        """)
        
        welcome_layout.addWidget(welcome_icon)
        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_subtitle)
        layout.addWidget(welcome_widget)

        # Chat display with modern styling
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("")
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background: rgba(30, 30, 46, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
                padding: 20px;
                color: #e8e8f0;
                font-size: 15px;
                line-height: 1.6;
            }
            QTextEdit QScrollBar:vertical {
                background: transparent;
                width: 6px;
                border-radius: 3px;
                margin: 4px 0;
            }
            QTextEdit QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 3px;
                min-height: 40px;
            }
            QTextEdit QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.25);
            }
        """)
        layout.addWidget(self.chat_display, 1)

        # Input area with glass effect
        input_container = QWidget()
        input_container.setStyleSheet("""
            QWidget {
                background: rgba(40, 40, 60, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 4px;
            }
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(12, 8, 12, 8)
        input_layout.setSpacing(12)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入您的指令，Jarvis 将帮您完成...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                padding: 8px 12px;
                color: #ffffff;
                font-size: 15px;
            }
            QLineEdit:focus {
                border: none;
            }
            QLineEdit:placeholder {
                color: rgba(255, 255, 255, 0.4);
            }
        """)
        
        self.send_btn = QPushButton("发送")
        self.send_btn.setFixedSize(80, 40)
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6366f1, stop:1 #8b5cf6);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #7c7ff2, stop:1 #9b7cf7);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5558e8, stop:1 #7b5ce3);
            }
            QPushButton:disabled {
                background: rgba(99, 102, 241, 0.4);
                color: rgba(255, 255, 255, 0.5);
            }
        """)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setFixedSize(80, 40)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: rgba(239, 68, 68, 0.8);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.9);
            }
        """)
        
        input_layout.addWidget(self.input_field, 1)
        input_layout.addWidget(self.send_btn)
        input_layout.addWidget(self.stop_btn)
        layout.addWidget(input_container)

        # Welcome message
        self.append_message("assistant", "👋 您好！我是 Jarvis。\n\n我可以帮助您完成各种计算机任务，只需告诉我您想要做什么。")

        # Connect signals
        self.send_btn.clicked.connect(self.send_message)
        self.input_field.returnPressed.connect(self.send_message)
        self.stop_btn.clicked.connect(self.stop_streaming)

    def append_message(self, role: str, content: str):
        """Append a styled message to the chat display."""
        if role == "user":
            html = f'''
            <div style="margin: 16px 0; display: flex; justify-content: flex-end;">
                <div style="max-width: 80%; padding: 14px 18px; 
                     background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6366f1, stop:1 #8b5cf6);
                     border-radius: 18px 18px 6px 18px; 
                     color: white; 
                     font-size: 15px;
                     line-height: 1.5;
                     box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);">
                    {content.replace('\n', '<br>')}
                </div>
            </div>
            '''
        else:
            html = f'''
            <div style="margin: 16px 0; display: flex; justify-content: flex-start;">
                <div style="max-width: 80%; padding: 14px 18px; 
                     background: rgba(50, 50, 70, 0.6);
                     border: 1px solid rgba(255, 255, 255, 0.08);
                     border-radius: 18px 18px 18px 6px; 
                     color: #e8e8f0; 
                     font-size: 15px;
                     line-height: 1.5;">
                    {content.replace('\n', '<br>')}
                </div>
            </div>
            '''
        self.chat_display.append(html)
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

    def send_message(self):
        msg = self.input_field.text().strip()
        if not msg or self.streaming:
            return

        self.append_message("user", msg)
        self.input_field.clear()
        self.messages.append({"role": "user", "content": msg})

        # Show typing indicator
        self.chat_display.append('''
            <div style="margin: 16px 0; display: flex; justify-content: flex-start;">
                <div style="padding: 14px 18px; 
                     background: rgba(50, 50, 70, 0.6);
                     border: 1px solid rgba(255, 255, 255, 0.08);
                     border-radius: 18px 18px 18px 6px;">
                    <span style="color: #888; font-size: 14px;">思考中<span id="dots">...</span></span>
                </div>
            </div>
        ''')
        
        self.streaming = True
        self.current_response = ""
        self.update_ui_state()

        try:
            client = get_client()
            
            self.thread = QThread()
            self.worker = StreamingWorker(client, self.messages.copy())
            self.worker.moveToThread(self.thread)
            
            self.thread.started.connect(self.worker.run)
            self.worker.chunk.connect(self.on_chunk)
            self.worker.finished.connect(self.on_finished)
            self.worker.error.connect(self.on_error)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            
            self.thread.start()
            
        except Exception as e:
            self.streaming = False
            self.append_message("assistant", f"❌ 连接错误: {str(e)}\n\n请检查您的 API 设置。")
            self.update_ui_state()

    def on_chunk(self, chunk: str):
        """Handle streaming chunk."""
        self.current_response += chunk
        
    def on_finished(self, full_response: str):
        """Handle streaming completion."""
        self.streaming = False
        self.messages.append({"role": "assistant", "content": full_response})
        
        # Remove typing indicator
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()
        
        self.append_message("assistant", full_response)
        self.update_ui_state()

    def on_error(self, error: str):
        """Handle streaming error."""
        self.streaming = False
        
        # Remove typing indicator
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()
        
        self.append_message("assistant", f"❌ 发生错误: {error}")
        self.update_ui_state()

    def stop_streaming(self):
        """Stop the current streaming."""
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

    def update_ui_state(self):
        """Update UI based on streaming state."""
        self.send_btn.setEnabled(not self.streaming)
        self.stop_btn.setEnabled(self.streaming)
        self.input_field.setEnabled(not self.streaming)

    def clear_chat(self):
        """Clear the chat history."""
        self.messages = []
        self.chat_display.clear()
        self.append_message("assistant", "✅ 对话已清空。请告诉我您想要完成什么任务？")
