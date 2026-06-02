# app/settings_window.py
"""Settings window for configuring Jarvis Agent."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QLabel, QTabWidget, QWidget, QGroupBox,
    QHBoxLayout, QCheckBox, QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from config.app_config import Config
from models.model_router import get_client, get_available_providers, get_provider_info


class SettingsWindow(QDialog):
    """Settings dialog for API keys, providers, and preferences."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setObjectName("settings")
        self.setModal(True)
        self.resize(500, 450)
        
        # Frameless with shadow
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        self._config = Config()
        self._init_ui()
        self._load_config()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("⚙️ 设置")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #e0e0ff; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # Tab widget
        tabs = QTabWidget()
        tabs.addTab(self._create_provider_tab(), "模型提供商")
        tabs.addTab(self._create_general_tab(), "通用设置")
        tabs.addTab(self._create_appearance_tab(), "外观")
        layout.addWidget(tabs)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn = QPushButton("保存")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50, stop:1 #388e3c);
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5cbf60, stop:1 #489e4c);
            }
        """)
        self.save_btn.clicked.connect(self._save_config)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)
        
        self.setStyleSheet("""
            QDialog#settings {
                background: rgba(25, 25, 35, 0.98);
                border-radius: 12px;
            }
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: rgba(40, 44, 55, 0.5);
                color: #a0a0b0;
                padding: 10px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: rgba(60, 64, 75, 0.8);
                color: #e0e0ff;
            }
            QTabBar::tab:hover:selected {
                background: rgba(70, 74, 85, 0.8);
            }
            QLabel {
                color: #c0c0d0;
            }
            QLineEdit, QComboBox, QSpinBox {
                background: rgba(40, 44, 55, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 6px;
                padding: 8px 12px;
                color: #e0e0ff;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #5a9cff;
            }
            QPushButton {
                background: rgba(60, 64, 75, 0.8);
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                color: #e0e0ff;
            }
            QPushButton:hover {
                background: rgba(70, 74, 85, 0.9);
            }
            QGroupBox {
                color: #a0a0b0;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

    def _create_provider_tab(self) -> QWidget:
        """Create provider configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # OpenAI settings
        openai_group = QGroupBox("OpenAI")
        openai_layout = QFormLayout()
        self.openai_key = QLineEdit()
        self.openai_key.setPlaceholderText("sk-...")
        self.openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_model = QComboBox()
        self.openai_model.addItems(["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"])
        openai_layout.addRow("API Key:", self.openai_key)
        openai_layout.addRow("模型:", self.openai_model)
        openai_group.setLayout(openai_layout)
        layout.addWidget(openai_group)
        
        # Anthropic settings
        anthropic_group = QGroupBox("Anthropic Claude")
        anthropic_layout = QFormLayout()
        self.anthropic_key = QLineEdit()
        self.anthropic_key.setPlaceholderText("sk-ant-...")
        self.anthropic_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.anthropic_model = QComboBox()
        self.anthropic_model.addItems(["claude-3-5-sonnet-20241022", "claude-3-5-sonnet-20240620", 
                                       "claude-3-opus-20240229", "claude-3-haiku-20240307"])
        anthropic_layout.addRow("API Key:", self.anthropic_key)
        anthropic_layout.addRow("模型:", self.anthropic_model)
        anthropic_group.setLayout(anthropic_layout)
        layout.addWidget(anthropic_group)
        
        # Ollama settings
        ollama_group = QGroupBox("Ollama (本地)")
        ollama_layout = QFormLayout()
        self.ollama_url = QLineEdit()
        self.ollama_url.setPlaceholderText("http://localhost:11434")
        self.ollama_model = QLineEdit()
        self.ollama_model.setPlaceholderText("llama3.2")
        ollama_layout.addRow("服务器地址:", self.ollama_url)
        ollama_layout.addRow("模型:", self.ollama_model)
        ollama_group.setLayout(ollama_layout)
        layout.addWidget(ollama_group)
        
        # Google settings
        google_group = QGroupBox("Google Gemini")
        google_layout = QFormLayout()
        self.google_key = QLineEdit()
        self.google_key.setPlaceholderText("Google API Key")
        self.google_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.google_model = QComboBox()
        self.google_model.addItems(["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"])
        google_layout.addRow("API Key:", self.google_key)
        google_layout.addRow("模型:", self.google_model)
        google_group.setLayout(google_layout)
        layout.addWidget(google_group)
        
        # Active provider selection
        provider_select = QGroupBox("激活的提供商")
        provider_layout = QFormLayout()
        self.active_provider = QComboBox()
        self.active_provider.addItems(get_available_providers())
        self.active_provider.currentIndexChanged.connect(self._on_provider_changed)
        provider_layout.addRow("使用:", self.active_provider)
        provider_select.setLayout(provider_layout)
        layout.addWidget(provider_select)
        
        layout.addStretch()
        return widget

    def _create_general_tab(self) -> QWidget:
        """Create general settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Agent settings
        agent_group = QGroupBox("代理设置")
        agent_layout = QFormLayout()
        self.max_retries = QSpinBox()
        self.max_retries.setRange(1, 10)
        self.max_retries.setValue(3)
        self.max_steps = QSpinBox()
        self.max_steps.setRange(10, 200)
        self.max_steps.setValue(50)
        self.auto_screenshot = QCheckBox("自动截取屏幕")
        self.auto_screenshot.setChecked(True)
        agent_layout.addRow("最大重试次数:", self.max_retries)
        agent_layout.addRow("最大步数:", self.max_steps)
        agent_layout.addRow("", self.auto_screenshot)
        agent_group.setLayout(agent_layout)
        layout.addWidget(agent_group)
        
        # Connection settings
        conn_group = QGroupBox("连接设置")
        conn_layout = QFormLayout()
        self.connection_timeout = QSpinBox()
        self.connection_timeout.setRange(10, 300)
        self.connection_timeout.setValue(60)
        self.connection_timeout.setSuffix(" 秒")
        conn_layout.addRow("超时时间:", self.connection_timeout)
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        layout.addStretch()
        return widget

    def _create_appearance_tab(self) -> QWidget:
        """Create appearance settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        info = QLabel("外观设置将很快推出...\n\n当前版本使用深色主题。")
        info.setStyleSheet("color: #888; font-size: 14px; padding: 20px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        layout.addStretch()
        return widget

    def _load_config(self):
        """Load configuration into UI."""
        # OpenAI
        self.openai_key.setText(self._config.get("api_key", ""))
        self.openai_model.setCurrentText(self._config.get("model_name", "gpt-4o-mini"))
        
        # Anthropic
        self.anthropic_key.setText(self._config.get("anthropic_api_key", ""))
        self.anthropic_model.setCurrentText(self._config.get("anthropic_model", "claude-3-5-sonnet-20241022"))
        
        # Ollama
        self.ollama_url.setText(self._config.get("ollama_url", "http://localhost:11434"))
        self.ollama_model.setText(self._config.get("ollama_model", "llama3.2"))
        
        # Google
        self.google_key.setText(self._config.get("google_api_key", ""))
        self.google_model.setCurrentText(self._config.get("google_model", "gemini-2.0-flash"))
        
        # Active provider
        provider = self._config.get("model_provider", "OpenAI")
        idx = self.active_provider.findText(provider)
        if idx >= 0:
            self.active_provider.setCurrentIndex(idx)
        
        # General settings
        self.max_retries.setValue(self._config.get("max_retries", 3))
        self.max_steps.setValue(self._config.get("max_steps", 50))
        self.connection_timeout.setValue(self._config.get("connection_timeout", 60))

    def _save_config(self):
        """Save configuration from UI."""
        # OpenAI
        self._config.set("api_key", self.openai_key.text().strip())
        self._config.set("model_name", self.openai_model.currentText())
        
        # Anthropic
        self._config.set("anthropic_api_key", self.anthropic_key.text().strip())
        self._config.set("anthropic_model", self.anthropic_model.currentText())
        
        # Ollama
        self._config.set("ollama_url", self.ollama_url.text().strip())
        self._config.set("ollama_model", self.ollama_model.text().strip())
        
        # Google
        self._config.set("google_api_key", self.google_key.text().strip())
        self._config.set("google_model", self.google_model.currentText())
        
        # Active provider
        self._config.set("model_provider", self.active_provider.currentText())
        
        # General
        self._config.set("max_retries", self.max_retries.value())
        self._config.set("max_steps", self.max_steps.value())
        self._config.set("connection_timeout", self.connection_timeout.value())
        
        QMessageBox.information(self, "设置", "设置已保存！")
        self.accept()

    def _on_provider_changed(self, index):
        """Handle provider selection change."""
        provider = self.active_provider.currentText()
        info = get_provider_info(provider)
        
        if info.get("requires_api_key", False):
            # Highlight required API key field
            pass

