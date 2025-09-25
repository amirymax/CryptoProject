from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QSpinBox
)
from crypto_core.classic import caesar


class CaesarTab(QWidget):
    """Вкладка для шифра Цезаря"""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Поле для ввода текста
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Введите текст...")
        layout.addWidget(QLabel("Исходный текст:"))
        layout.addWidget(self.input_text)

        # Сдвиг (ключ)
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Сдвиг:"))
        self.shift_input = QSpinBox()
        self.shift_input.setRange(0, len(caesar.ALPHABET) - 1)
        key_layout.addWidget(self.shift_input)
        layout.addLayout(key_layout)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.encrypt_btn = QPushButton("Зашифровать")
        self.decrypt_btn = QPushButton("Расшифровать")
        btn_layout.addWidget(self.encrypt_btn)
        btn_layout.addWidget(self.decrypt_btn)
        layout.addLayout(btn_layout)

        # Результат
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(QLabel("Результат:"))
        layout.addWidget(self.output_text)

        self.setLayout(layout)

        # Сигналы
        self.encrypt_btn.clicked.connect(self.encrypt_text)
        self.decrypt_btn.clicked.connect(self.decrypt_text)

    def encrypt_text(self):
        text = self.input_text.toPlainText()
        shift = self.shift_input.value()
        encrypted = caesar.encrypt(text, shift)
        self.output_text.setPlainText(encrypted)

    def decrypt_text(self):
        text = self.input_text.toPlainText()
        shift = self.shift_input.value()
        decrypted = caesar.decrypt(text, shift)
        self.output_text.setPlainText(decrypted)
