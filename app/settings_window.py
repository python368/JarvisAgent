# app/settings_window.py
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QLabel,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from config.app_config import Config
from models.model_router import get_client


class SettingsWindow(QDialog):
    """Settings dialog for API key, provider, model, and Ollama URL."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setObjectName("settings")
        self.setModal(True)
        self.resize(420, 300)
        # Apply fluid glass effect to the dialog
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150)) # 半透明黑色阴影
        shadow.setOffset(0, 0) # 阴影居中
        self.setGraphicsEffect(shadow)

        self._config = Config()
        self._init_ui()
        self._load_config()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setHorizontalSpacing(15)
        form.setVerticalSpacing(10)
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("OpenAI API Key")
        form.addRow("API Key:", self.api_key_input)

        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["OpenAI", "Ollama"])
        form.addRow("Provider:", self.provider_combo)

        # Model selector – will be populated based on provider
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        form.addRow("Model:", self.model_combo)

        # Refresh button to fetch available models from the provider
        self.refresh_btn = QPushButton("刷新模型列表")
        form.addRow(self.refresh_btn)

        self.ollama_url_input = QLineEdit()
        self.ollama_url_input.setPlaceholderText("Ollama URL, e.g., http://localhost:11434")
        form.addRow("Ollama URL:", self.ollama_url_input)

        layout.addLayout(form)

        self.save_btn = QPushButton("保存")
        self.save_btn.setObjectName("saveButton")
        self.save_btn.clicked.connect(self._save_config)
        layout.addWidget(self.save_btn)

        self.provider_combo.currentIndexChanged.connect(self.refresh_models)
        self.refresh_btn.clicked.connect(self.refresh_models)

        self.setStyleSheet(self._get_qss_style())

    def _load_config(self):
        self.api_key_input.setText(self._config.get("api_key"))
        self.provider_combo.setCurrentText(self._config.get("model_provider"))
        # Populate model list based on provider and set selected model
        self.refresh_models()
        current_model = self._config.get("model_name")
        if current_model:
            idx = self.model_combo.findText(current_model)
            if idx >= 0:
                self.model_combo.setCurrentIndex(idx)
            else:
                # If not in list, add it as editable entry
                self.model_combo.addItem(current_model)
                self.model_combo.setCurrentText(current_model)
        self.ollama_url_input.setText(self._config.get("ollama_url"))

    def _get_qss_style(self):
        return """
            QDialog#settings {
                background-color: #1a1a1a;
                border-radius: 5px;
                border: none;
            }

            QLabel {
                color: #cccccc;
                font-size: 13px;
                padding-left: 5px;
            }

            QLineEdit {
                background-color: #2b2b2b;
                border: 1px solid #444444;
                border-radius: 4px;
                color: #eeeeee;
                padding: 6px 8px;
                font-size: 13px;
            }

            QLineEdit:hover {
                border: 1px solid #555555;
            }

            QLineEdit:focus {
                border: 1px solid #007acc;
            }

            QComboBox {
                background-color: #2b2b2b;
                border: 1px solid #444444;
                border-radius: 4px;
                color: #eeeeee;
                padding: 6px 8px;
                font-size: 13px;
                selection-background-color: #007acc;
            }

            QComboBox:hover {
                border: 1px solid #555555;
            }

            QComboBox:focus {
                border: 1px solid #007acc;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 18px;
                border-left-width: 1px;
                border-left-color: #444444;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }

            QComboBox::down-arrow {
                image: url(:/icons/down_arrow.png); /* 假设存在资源文件 */
            }

            QPushButton {
                background-color: #007acc;
                border: none;
                border-radius: 4px;
                color: #ffffff;
                padding: 7px 12px;
                font-size: 13px;
            }

            QPushButton:hover {
                background-color: #0088e6;
            }

            QPushButton:pressed {
                background-color: #006bb3;
            }

            QPushButton#saveButton {
                background-color: #28a745; /* 绿色保存按钮 */
            }

            QPushButton#saveButton:hover {
                background-color: #218838;
            }

            QPushButton#saveButton:pressed {
                background-color: #1e7e34;
            }
        """

    def _save_config(self):
        self._config.set("api_key", self.api_key_input.text().strip())
        self._config.set("model_provider", self.provider_combo.currentText())
        self._config.set("model_name", self.model_combo.currentText().strip())
        self._config.set("ollama_url", self.ollama_url_input.text().strip())
        self.accept()

    # ---------------------------------------------------------------------
    # Helper methods
    # ---------------------------------------------------------------------
    def refresh_models(self):
        """Refresh the model list based on the selected provider.

        The method attempts to instantiate a client via :func:`models.model_router.get_client`
        and query its ``list_models`` method.  If the call fails (e.g., missing API key),
        the combo box is cleared and a placeholder entry is added.
        """
        self.model_combo.clear()
        provider = self.provider_combo.currentText()
        # Temporarily set a placeholder while loading
        self.model_combo.addItem("加载中…")
        try:
            client = get_client()
            models = client.list_models()
            self.model_combo.clear()
            if models:
                self.model_combo.addItems(models)
            else:
                self.model_combo.addItem("无可用模型")
        except Exception:
            # Fallback: allow manual entry
            self.model_combo.clear()
            self.model_combo.setEditable(True)
            self.model_combo.addItem("手动输入模型名称")

