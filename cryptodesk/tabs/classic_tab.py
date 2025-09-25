from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QLineEdit,
    QPushButton, QHBoxLayout, QMessageBox
)

from crypto_core.classic import more_ciphers


class ClassicTab(QWidget):
    """
    Вкладка: Классические шифры (замена, перестановка, гаммирование)
    """

    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        # ============ Шифр замены ============
        self.layout().addWidget(QLabel("🔠 Шифр замены"))
        self.sub_input = QTextEdit()
        self.sub_input.setPlaceholderText("Введите текст...")
        self.layout().addWidget(self.sub_input)

        sub_key_row = QHBoxLayout()
        self.sub_key = QLineEdit()
        self.sub_key.setPlaceholderText("Введите ключ-алфавит (33 буквы, без 'ё')")
        self.sub_enc_btn = QPushButton("Зашифровать")
        self.sub_dec_btn = QPushButton("Расшифровать")
        sub_key_row.addWidget(self.sub_key)
        sub_key_row.addWidget(self.sub_enc_btn)
        sub_key_row.addWidget(self.sub_dec_btn)
        self.layout().addLayout(sub_key_row)

        # ============ Шифр перестановки ============
        self.layout().addWidget(QLabel("🔀 Шифр перестановки"))
        self.trans_input = QTextEdit()
        self.trans_input.setPlaceholderText("Введите текст...")
        self.layout().addWidget(self.trans_input)

        trans_key_row = QHBoxLayout()
        self.trans_key = QLineEdit()
        self.trans_key.setPlaceholderText("Ключ (например: 2,0,1)")
        self.trans_enc_btn = QPushButton("Зашифровать")
        self.trans_dec_btn = QPushButton("Расшифровать")
        trans_key_row.addWidget(self.trans_key)
        trans_key_row.addWidget(self.trans_enc_btn)
        trans_key_row.addWidget(self.trans_dec_btn)
        self.layout().addLayout(trans_key_row)

        # ============ Шифр гаммирования ============
        self.layout().addWidget(QLabel("🎲 Шифр гаммирования"))
        self.gamma_input = QTextEdit()
        self.gamma_input.setPlaceholderText("Введите текст...")
        self.layout().addWidget(self.gamma_input)

        gamma_key_row = QHBoxLayout()
        self.gamma_key = QLineEdit()
        self.gamma_key.setPlaceholderText("Введите гамму (строка-ключ)")
        self.gamma_enc_btn = QPushButton("Зашифровать")
        self.gamma_dec_btn = QPushButton("Расшифровать")
        gamma_key_row.addWidget(self.gamma_key)
        gamma_key_row.addWidget(self.gamma_enc_btn)
        gamma_key_row.addWidget(self.gamma_dec_btn)
        self.layout().addLayout(gamma_key_row)

        # ============ Лог ============
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.layout().addWidget(QLabel("Лог:"))
        self.layout().addWidget(self.log)

        # Сигналы
        self.sub_enc_btn.clicked.connect(self.on_sub_enc)
        self.sub_dec_btn.clicked.connect(self.on_sub_dec)
        self.trans_enc_btn.clicked.connect(self.on_trans_enc)
        self.trans_dec_btn.clicked.connect(self.on_trans_dec)
        self.gamma_enc_btn.clicked.connect(self.on_gamma_enc)
        self.gamma_dec_btn.clicked.connect(self.on_gamma_dec)

    def write_log(self, text: str):
        self.log.append(text)
        self.log.ensureCursorVisible()

    # ---------------- Шифр замены ----------------
    def on_sub_enc(self):
        text = self.sub_input.toPlainText().lower()
        key = self.sub_key.text().lower()
        if len(key) != len(more_ciphers.RUS_ALPHABET_NOYO):
            QMessageBox.warning(self, "Ошибка", "Ключ-алфавит должен содержать 33 буквы (без 'ё').")
            return
        res = more_ciphers.substitution_encrypt(text, key)
        self.write_log(f"Шифр замены (ENC): {res}")

    def on_sub_dec(self):
        text = self.sub_input.toPlainText().lower()
        key = self.sub_key.text().lower()
        if len(key) != len(more_ciphers.RUS_ALPHABET_NOYO):
            QMessageBox.warning(self, "Ошибка", "Ключ-алфавит должен содержать 33 буквы (без 'ё').")
            return
        res = more_ciphers.substitution_decrypt(text, key)
        self.write_log(f"Шифр замены (DEC): {res}")

    # ---------------- Шифр перестановки ----------------
    def on_trans_enc(self):
        text = self.trans_input.toPlainText()
        try:
            key = [int(x) for x in self.trans_key.text().split(",")]
        except Exception:
            QMessageBox.warning(self, "Ошибка", "Ключ должен быть вида: 2,0,1")
            return
        res = more_ciphers.transposition_encrypt(text, key)
        self.write_log(f"Перестановка (ENC): {res}")

    def on_trans_dec(self):
        text = self.trans_input.toPlainText()
        try:
            key = [int(x) for x in self.trans_key.text().split(",")]
        except Exception:
            QMessageBox.warning(self, "Ошибка", "Ключ должен быть вида: 2,0,1")
            return
        res = more_ciphers.transposition_decrypt(text, key)
        self.write_log(f"Перестановка (DEC): {res}")

    # ---------------- Шифр гаммирования ----------------
    def on_gamma_enc(self):
        text = self.gamma_input.toPlainText().lower()
        gamma = self.gamma_key.text().lower()
        if not gamma:
            QMessageBox.warning(self, "Ошибка", "Введите гамму (ключ).")
            return
        res = more_ciphers.gamma_encrypt(text, gamma)
        self.write_log(f"Гаммирование (ENC): {res}")

    def on_gamma_dec(self):
        text = self.gamma_input.toPlainText().lower()
        gamma = self.gamma_key.text().lower()
        if not gamma:
            QMessageBox.warning(self, "Ошибка", "Введите гамму (ключ).")
            return
        res = more_ciphers.gamma_decrypt(text, gamma)
        self.write_log(f"Гаммирование (DEC): {res}")
