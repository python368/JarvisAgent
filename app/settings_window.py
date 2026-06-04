# app/settings_window.py
"""Settings window for JarvisAgent configuration."""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QTabWidget, 
                             QWidget, QFormLayout, QGroupBox, QScrollArea,
                             QMessageBox)
from PyQt6.QtGui import QFont

from config.app_config import Config
from models.model_router import get_available_providers


class SettingsWindow(QDialog):
    """Settings dialog for configuring JarvisAgent."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        self.setWindowTitle("设置")
        self.setFixedSize(560, 500)
        self.setStyleSheet("""
            QDialog {
                background: rgba(20, 20, 35, 0.98);
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header = QLabel("⚙️ 设置")
        header.setStyleSheet("""
            color: #ffffff;
            font-size: 24px;
            font-weight: 700;
            padding-bottom: 10px;
        """)
        layout.addWidget(header)

        # Tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                background: rgba(30, 30, 50, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 16px;
            }
            QTabBar::tab {
                background: transparent;
                color: rgba(255, 255, 255, 0.6);
                padding: 12px 24px;
                font-size: 14px;
                border: none;
            }
            QTabBar::tab:selected {
                color: #ffffff;
                background: rgba(99, 102, 241, 0.2);
                border-radius: 8px;
            }
            QTabBar::tab:hover:!selected {
                background: rgba(255, 255, 255, 0.05);
            }
        """)

        # Provider settings tab
        provider_tab = self._create_provider_tab()
        tabs.addTab(provider_tab, "🤖 AI 模型")

        # General settings tab
        general_tab = self._create_general_tab()
        tabs.addTab(general_tab, "⚡ 通用")

        layout.addWidget(tabs, 1)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_save = QPushButton("保存设置")
        self.btn_save.setFixedSize(120, 42)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #8b5cf6);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7c7ff2, stop:1 #9b7cf7);
            }
        """)
        self.btn_save.clicked.connect(self.save_settings)
        btn_layout.addWidget(self.btn_save)

        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.setFixedSize(100, 42)
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.15);
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

    def _create_provider_tab(self) -> QWidget:
        """Create provider settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Provider selection
        provider_group = QGroupBox("AI 提供商")
        provider_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-size: 14px;
                font-weight: 600;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 16px;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }
        """)

        provider_layout = QFormLayout(provider_group)
        provider_layout.setSpacing(16)
        provider_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Provider dropdown
        self.provider_combo = QComboBox()
        self.provider_combo.setFixedHeight(44)
        providers = get_available_providers()
        self.provider_combo.addItems(providers)
        
        current_provider = self.config.get("model_provider", "OpenAI")
        if current_provider in providers:
            self.provider_combo.setCurrentText(current_provider)
        
        self.provider_combo.setStyleSheet("""
            QComboBox {
                background: rgba(50, 50, 75, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 10px;
                padding: 0 16px;
                color: #ffffff;
                font-size: 14px;
                min-width: 200px;
            }
            QComboBox:hover {
                border-color: rgba(99, 102, 241, 0.5);
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 12px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid rgba(255, 255, 255, 0.5);
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background: rgba(40, 40, 65, 0.98);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                selection-background-color: rgba(99, 102, 241, 0.4);
                padding: 8px;
            }
        """)
        provider_layout.addRow("选择提供商:", self.provider_combo)

        # API Key input
        self.api_key_input = QLineEdit()
        self.api_key_input.setFixedHeight(44)
        self.api_key_input.setPlaceholderText("输入您的 API Key")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setText(self.config.get("api_key", ""))
        self.api_key_input.setStyleSheet("""
            QLineEdit {
                background: rgba(50, 50, 75, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 10px;
                padding: 0 16px;
                color: #ffffff;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #6366f1;
            }
            QLineEdit:placeholder {
                color: rgba(255, 255, 255, 0.4);
            }
        """)
        provider_layout.addRow("API Key:", self.api_key_input)

        # Ollama URL (shown for Ollama provider)
        self.ollama_layout = QFormLayout()
        self.ollama_url_input = QLineEdit()
        self.ollama_url_input.setFixedHeight(44)
        self.ollama_url_input.setPlaceholderText("http://localhost:11434")
        self.ollama_url_input.setText(self.config.get("ollama_url", "http://localhost:11434"))
        self.ollama_url_input.setStyleSheet("""
            QLineEdit {
                background: rgba(50, 50, 75, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 10px;
                padding: 0 16px;
                color: #ffffff;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #6366f1;
            }
        """)
        self.ollama_layout.addRow("服务器地址:", self.ollama_url_input)
        
        layout.addWidget(provider_group)

        # Model selection
        model_group = QGroupBox("模型选择")
        model_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-size: 14px;
                font-weight: 600;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 16px;
                margin-top: 8px;
            }
        """)

        model_layout = QFormLayout(model_group)
        model_layout.setSpacing(16)

        self.model_combo = QComboBox()
        self.model_combo.setFixedHeight(44)
        self._update_model_list()
        self.model_combo.setStyleSheet("""
            QComboBox {
                background: rgba(50, 50, 75, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 10px;
                padding: 0 16px;
                color: #ffffff;
                font-size: 14px;
                min-width: 200px;
            }
            QComboBox QAbstractItemView {
                background: rgba(40, 40, 65, 0.98);
                border: 1px solid rgba(255, 255, 255, 0.1);
                selection-background-color: rgba(99, 102, 241, 0.4);
            }
        """)
        model_layout.addRow("选择模型:", self.model_combo)

        layout.addWidget(model_group)
        layout.addStretch()

        # Connect provider change
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)

        return widget

    def _create_general_tab(self) -> QWidget:
        """Create general settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        info = QLabel("通用设置功能开发中...\n\n当前版本支持基本的模型配置。")
        info.setStyleSheet("""
            color: rgba(255, 255, 255, 0.5);
            font-size: 14px;
            line-height: 1.8;
        """)
        layout.addWidget(info)
        layout.addStretch()

        return widget

    def _on_provider_changed(self, provider: str):
        """Handle provider change."""
        self._update_model_list()

    def _update_model_list(self):
        """Update available models based on selected provider."""
        self.model_combo.clear()
        
        provider = self.provider_combo.currentText()
        models = {
            "OpenAI": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
            "Anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-sonnet-latest", "claude-3-opus-latest", "claude-3-haiku-latest"],
            "Google": ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"],
            "Ollama": ["llama3.2", "llama3.1", "mistral", "codellama", "qwen2.5"],
        }
        
        model_list = models.get(provider, [])
        self.model_combo.addItems(model_list)
        
        # Set current model
        current_model = self.config.get("model_name", "")
        if current_model in model_list:
            self.model_combo.setCurrentText(current_model)

    def save_settings(self):
        """Save settings to config."""
        self.config.set("model_provider", self.provider_combo.currentText())
        self.config.set("model_name", self.model_combo.currentText())
        self.config.set("api_key", self.api_key_input.text())
        self.config.set("ollama_url", self.ollama_url_input.text())
        self.config.save()
        
        QMessageBox.information(self, "保存成功", "设置已保存！\n\n请重启应用以使更改生效。")
        self.accept()
