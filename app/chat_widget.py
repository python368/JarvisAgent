# app/chat_widget.py
"""Chat widget for user interaction with the Jarvis agent."""

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QLabel

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
            # Use async generator in a sync context
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
    """Main chat interface for user interaction."""
    
    def __init__(self):
        super().__init__()
        self.messages = []
        self.streaming = False
        self.current_response = ""
        self.worker = None
        self.thread = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Header with model info
        header = QLabel("💬 对话")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0ff; padding: 5px;")
        layout.addWidget(header)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("输入您的指令，Jarvis 将帮助您完成任务...")
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background: rgba(25, 25, 35, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 15px;
                color: #e0e0ff;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        layout.addWidget(self.chat_display)

        # Welcome message
        self.append_message("assistant", "👋 您好！我是 Jarvis，您的 AI 计算机助手。\n\n请描述您想要完成的任务，我将帮您执行。")

        # Input area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入指令...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: rgba(40, 44, 55, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 8px;
                padding: 12px 16px;
                color: #e0e0ff;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #5a9cff;
                background: rgba(45, 50, 62, 0.7);
            }
            QLineEdit:placeholder {
                color: rgba(255, 255, 255, 0.4);
            }
        """)
        
        self.send_btn = QPushButton("发送")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a86e8, stop:1 #3b6fc4);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a96f8, stop:1 #4a7fd4);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a76b4, stop:1 #2a5ea4);
            }
            QPushButton:disabled {
                background: rgba(74, 134, 232, 0.4);
            }
        """)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 80, 80, 0.8);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255, 90, 90, 0.9);
            }
        """)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        input_layout.addWidget(self.stop_btn)
        layout.addLayout(input_layout)

        # Connect signals
        self.send_btn.clicked.connect(self.send_message)
        self.input_field.returnPressed.connect(self.send_message)
        self.stop_btn.clicked.connect(self.stop_streaming)

    def append_message(self, role: str, content: str):
        """Append a message to the chat display."""
        if role == "user":
            html = f'''
            <div style="display: flex; justify-content: flex-end; margin: 8px 0;">
                <div style="max-width: 75%; padding: 12px 16px; background: linear-gradient(135deg, #4a86e8, #3b6fc4); 
                     border-radius: 16px 16px 4px 16px; color: white; line-height: 1.4;">
                    <b>您:</b><br>{content.replace(chr(10), '<br>')}
                </div>
            </div>
            '''
        else:
            html = f'''
            <div style="display: flex; justify-content: flex-start; margin: 8px 0;">
                <div style="max-width: 75%; padding: 12px 16px; background: rgba(40, 44, 55, 0.8); 
                     border-radius: 16px 16px 16px 4px; color: #e0e0ff; line-height: 1.4;">
                    <b>🤖 Jarvis:</b><br>{content.replace(chr(10), '<br>')}
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

        # Show thinking indicator
        self.assistant_html = '''
        <div style="display: flex; justify-content: flex-start; margin: 8px 0;">
            <div style="max-width: 75%; padding: 12px 16px; background: rgba(40, 44, 55, 0.8); 
                 border-radius: 16px 16px 16px 4px; color: #888; line-height: 1.4;">
                <b>🤖 Jarvis:</b><br><span id="thinking">思考中...</span>
            </div>
        </div>
        '''
        self.chat_display.append(self.assistant_html)
        self.streaming = True
        self.current_response = ""
        self.update_ui_state()

        # Start streaming
        try:
            client = get_client()
            
            # Create worker for background processing
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
            self.append_message("assistant", f"错误: {str(e)}")
            self.update_ui_state()

    def on_chunk(self, chunk: str):
        """Handle streaming chunk."""
        self.current_response += chunk
        
    def on_finished(self, full_response: str):
        """Handle streaming completion."""
        self.streaming = False
        self.messages.append({"role": "assistant", "content": full_response})
        
        # Remove thinking indicator and show response
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deleteChar()
        
        # Remove last assistant message placeholder
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()
        
        self.append_message("assistant", full_response)
        self.update_ui_state()

    def on_error(self, error: str):
        """Handle streaming error."""
        self.streaming = False
        # Remove thinking indicator
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deleteChar()
        
        self.append_message("assistant", f"错误: {error}")
        self.update_ui_state()

    def stop_streaming(self):
        """Stop the current streaming."""
        if self.thread and self.thread.isRunning():
            self.worker.error.emit("用户停止了请求")
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
        self.append_message("assistant", "对话已清空。请描述您想要完成的任务。")
