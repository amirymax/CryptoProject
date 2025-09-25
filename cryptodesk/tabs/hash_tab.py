import os
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout,
    QFileDialog, QMessageBox, QLineEdit, QComboBox
)

from crypto_core.hashing import hashing
from crypto_core.asymmetric import rsa, elgamal


class HashTab(QWidget):
    """
    Вкладка для работы с хэшами и цифровыми подписями
    """

    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        # Текст / файл для хэширования
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Введите текст для хэширования или подписи...")
        self.layout().addWidget(QLabel("Текст / содержимое файла:"))
        self.layout().addWidget(self.input_text)

        file_row = QHBoxLayout()
        self.load_file_btn = QPushButton("Загрузить файл")
        self.hash_alg_box = QComboBox()
        self.hash_alg_box.addItems(["MD5", "SHA256"])
        file_row.addWidget(self.load_file_btn)
        file_row.addWidget(QLabel("Алгоритм:"))
        file_row.addWidget(self.hash_alg_box)
        self.layout().addLayout(file_row)

        # Кнопки действий
        act_row = QHBoxLayout()
        self.hash_btn = QPushButton("Посчитать хэш")
        self.sign_btn = QPushButton("Подписать (RSA)")
        self.verify_btn = QPushButton("Проверить подпись (RSA)")
        act_row.addWidget(self.hash_btn)
        act_row.addWidget(self.sign_btn)
        act_row.addWidget(self.verify_btn)
        self.layout().addLayout(act_row)

        # Путь к ключам
        key_row = QHBoxLayout()
        self.privkey_input = QLineEdit()
        self.privkey_input.setPlaceholderText("Путь к приватному ключу PEM (для подписи)")
        self.privkey_input.setReadOnly(True)
        self.choose_priv_btn = QPushButton("Выбрать privkey")
        key_row.addWidget(self.privkey_input)
        key_row.addWidget(self.choose_priv_btn)
        self.layout().addLayout(key_row)

        pub_row = QHBoxLayout()
        self.pubkey_input = QLineEdit()
        self.pubkey_input.setPlaceholderText("Путь к публичному ключу PEM (для проверки подписи)")
        self.pubkey_input.setReadOnly(True)
        self.choose_pub_btn = QPushButton("Выбрать pubkey")
        pub_row.addWidget(self.pubkey_input)
        pub_row.addWidget(self.choose_pub_btn)
        self.layout().addLayout(pub_row)

        # Лог
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.layout().addWidget(QLabel("Лог:"))
        self.layout().addWidget(self.log)

        # Сигналы
        self.load_file_btn.clicked.connect(self.on_load_file)
        self.hash_btn.clicked.connect(self.on_hash)
        self.sign_btn.clicked.connect(self.on_sign)
        self.verify_btn.clicked.connect(self.on_verify)
        self.choose_priv_btn.clicked.connect(self.on_choose_privkey)
        self.choose_pub_btn.clicked.connect(self.on_choose_pubkey)

        # Данные
        self._current_bytes: Optional[bytes] = None
        self._last_signature: Optional[bytes] = None

    def write_log(self, text: str):
        self.log.append(text)
        self.log.ensureCursorVisible()

    def on_load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", os.getcwd(), "All Files (*)")
        if not path:
            return
        try:
            with open(path, "rb") as f:
                data = f.read()
            self._current_bytes = data
            self.input_text.setPlainText(data.decode("utf-8", errors="ignore"))
            self.write_log(f"Загружен файл: {Path(path).name} ({len(data)} байт)")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{e}")

    def on_hash(self):
        text = self.input_text.toPlainText().encode("utf-8")
        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите текст или загрузите файл.")
            return
        algo = self.hash_alg_box.currentText()
        digest = hashing.hash_bytes(text, algo.lower())
        self._current_bytes = text
        self.write_log(f"{algo} хэш: {digest}")

    def on_sign(self):
        if not self._current_bytes:
            QMessageBox.warning(self, "Ошибка", "Сначала введите текст или загрузите файл.")
            return
        priv_path = self.privkey_input.text().strip()
        if not priv_path:
            QMessageBox.warning(self, "Ошибка", "Укажите приватный ключ для подписи.")
            return
        try:
            priv = rsa.load_private_key(priv_path)
            signature = rsa.sign(self._current_bytes, priv)
            self._last_signature = signature
            sig_file = "signature.bin"
            with open(sig_file, "wb") as f:
                f.write(signature)
            self.write_log(f"Подпись (RSA) сохранена в {sig_file}")
            QMessageBox.information(self, "OK", f"Подпись сохранена: {sig_file}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подписи:\n{e}")

    def on_verify(self):
        if not self._current_bytes:
            QMessageBox.warning(self, "Ошибка", "Нет данных для проверки.")
            return
        pub_path = self.pubkey_input.text().strip()
        if not pub_path:
            QMessageBox.warning(self, "Ошибка", "Укажите публичный ключ для проверки.")
            return
        if not self._last_signature:
            QMessageBox.warning(self, "Ошибка", "Нет подписи для проверки (подпишите данные).")
            return
        try:
            pub = rsa.load_public_key(pub_path)
            ok = rsa.verify(self._current_bytes, self._last_signature, pub)
            if ok:
                self.write_log("✅ Подпись корректна")
                QMessageBox.information(self, "OK", "Подпись корректна ✅")
            else:
                self.write_log("❌ Подпись НЕверна")
                QMessageBox.warning(self, "Ошибка", "Подпись НЕверна ❌")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка проверки подписи:\n{e}")

    def on_choose_privkey(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите приватный ключ (PEM)", os.getcwd(), "PEM Files (*.pem)")
        if path:
            self.privkey_input.setText(path)

    def on_choose_pubkey(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите публичный ключ (PEM)", os.getcwd(), "PEM Files (*.pem)")
        if path:
            self.pubkey_input.setText(path)
