import os
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout,
    QFileDialog, QMessageBox, QLineEdit
)

# crypto core
from crypto_core.hybrid import hybrid_rsa
from crypto_core.asymmetric import rsa as rsa_module


class FilesTab(QWidget):
    """
    Вкладка для работы с файлами:
    - загрузка .txt/.docx (как байтов)
    - гибридное шифрование AES-GCM + RSA (публичный ключ)
    - локальное сохранение зашифрованного контейнера (.cvc)
    - расшифровка при наличии приватного ключа
    """

    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        # путь к файлу
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("Путь к файлу (txt/docx)...")
        self.file_path_input.setReadOnly(True)
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.file_path_input)

        self.load_btn = QPushButton("Загрузить файл")
        btn_row.addWidget(self.load_btn)
        self.layout().addLayout(btn_row)

        # кнопки действий
        act_row = QHBoxLayout()
        self.encrypt_btn = QPushButton("Зашифровать (AES+RSA)")
        self.decrypt_btn = QPushButton("Дешифровать (RSA priv)")
        act_row.addWidget(self.encrypt_btn)
        act_row.addWidget(self.decrypt_btn)
        self.layout().addLayout(act_row)

        # публичный ключ
        key_row = QHBoxLayout()
        self.pubkey_input = QLineEdit()
        self.pubkey_input.setPlaceholderText("Путь к публичному ключу (PEM) для шифрования")
        self.pubkey_input.setReadOnly(True)
        self.choose_pub_btn = QPushButton("Выбрать pubkey")
        self.gen_keys_btn = QPushButton("Сгенерировать ключи")
        key_row.addWidget(self.pubkey_input)
        key_row.addWidget(self.choose_pub_btn)
        key_row.addWidget(self.gen_keys_btn)
        self.layout().addLayout(key_row)

        # приватный ключ
        priv_row = QHBoxLayout()
        self.privkey_input = QLineEdit()
        self.privkey_input.setPlaceholderText("Путь к приватному ключу (PEM) для дешифровки")
        self.privkey_input.setReadOnly(True)
        self.choose_priv_btn = QPushButton("Выбрать privkey")
        priv_row.addWidget(self.privkey_input)
        priv_row.addWidget(self.choose_priv_btn)
        self.layout().addLayout(priv_row)

        # лог
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.layout().addWidget(QLabel("Лог:"))
        self.layout().addWidget(self.log)

        # сигналы
        self.load_btn.clicked.connect(self.on_load_file)
        self.choose_pub_btn.clicked.connect(self.on_choose_pubkey)
        self.choose_priv_btn.clicked.connect(self.on_choose_privkey)
        self.gen_keys_btn.clicked.connect(self.on_generate_keys)
        self.encrypt_btn.clicked.connect(self.on_encrypt)
        self.decrypt_btn.clicked.connect(self.on_decrypt)

        # внутренние переменные
        self._file_bytes: Optional[bytes] = None
        self._file_name: Optional[str] = None

    def write_log(self, text: str):
        self.log.append(text)
        self.log.ensureCursorVisible()

    def on_load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", os.getcwd(),
                                              "Text and Docx Files (*.txt *.docx);;All Files (*)")
        if not path:
            return
        try:
            with open(path, "rb") as f:
                data = f.read()
            self._file_bytes = data
            self._file_name = Path(path).name
            self.file_path_input.setText(path)
            self.write_log(f"Файл загружен: {self._file_name} ({len(data)} байт)")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{e}")

    def on_choose_pubkey(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите публичный ключ (PEM)", os.getcwd(),
                                              "PEM Files (*.pem);;All Files (*)")
        if path:
            self.pubkey_input.setText(path)

    def on_choose_privkey(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите приватный ключ (PEM)", os.getcwd(),
                                              "PEM Files (*.pem);;All Files (*)")
        if path:
            self.privkey_input.setText(path)

    def on_generate_keys(self):
        try:
            priv, pub = rsa_module.generate_keys()
            rsa_module.save_private_key(priv, "private.pem")
            rsa_module.save_public_key(pub, "public.pem")

            priv_path = str(Path("private.pem").absolute())
            pub_path = str(Path("public.pem").absolute())

            self.pubkey_input.setText(pub_path)
            self.privkey_input.setText(priv_path)

            self.write_log("Новая пара ключей сгенерирована: private.pem и public.pem")
            QMessageBox.information(
                self,
                "OK",
                f"Ключи сгенерированы:\n{priv_path}\n{pub_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сгенерировать ключи:\n{e}")

    def _load_public_key_obj(self, path: str):
        return rsa_module.load_public_key(path)

    def _load_private_key_obj(self, path: str, password: Optional[str] = None):
        return rsa_module.load_private_key(path, password=password)

    def on_encrypt(self):
        if not self._file_bytes:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите файл.")
            return
        pub_path = self.pubkey_input.text().strip()
        if not pub_path:
            QMessageBox.warning(self, "Ошибка", "Выберите или сгенерируйте публичный ключ.")
            return
        try:
            pub = self._load_public_key_obj(pub_path)
            payload = hybrid_rsa.hybrid_encrypt(pub, self._file_bytes)

            out_name = f"{self._file_name}.cvc"
            enc_key = payload["enc_key"]; iv = payload["iv"]; tag = payload["tag"]; ciphertext = payload["ciphertext"]

            with open(out_name, "wb") as f:
                f.write(len(enc_key).to_bytes(4, "big")); f.write(enc_key)
                f.write(len(iv).to_bytes(2, "big")); f.write(iv)
                f.write(len(tag).to_bytes(1, "big")); f.write(tag)
                f.write(len(ciphertext).to_bytes(8, "big")); f.write(ciphertext)

            self.write_log(f"Файл зашифрован и сохранён: {out_name}")
            QMessageBox.information(self, "OK", f"Файл зашифрован и сохранён: {out_name}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка шифрования:\n{e}")

    def on_decrypt(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите зашифрованный контейнер (.cvc)", os.getcwd(),
                                              "Crypto Vault Container (*.cvc);;All Files (*)")
        if not path:
            return
        priv_path = self.privkey_input.text().strip()
        if not priv_path:
            QMessageBox.warning(self, "Ошибка", "Выберите приватный ключ для дешифровки.")
            return
        try:
            priv = self._load_private_key_obj(priv_path)
            with open(path, "rb") as f:
                b = f.read()
            idx = 0
            enc_key_len = int.from_bytes(b[idx:idx+4], "big"); idx += 4
            enc_key = b[idx:idx+enc_key_len]; idx += enc_key_len
            iv_len = int.from_bytes(b[idx:idx+2], "big"); idx += 2
            iv = b[idx:idx+iv_len]; idx += iv_len
            tag_len = int.from_bytes(b[idx:idx+1], "big"); idx += 1
            tag = b[idx:idx+tag_len]; idx += tag_len
            ciphertext_len = int.from_bytes(b[idx:idx+8], "big"); idx += 8
            ciphertext = b[idx:idx+ciphertext_len]; idx += ciphertext_len

            container = {"enc_key": enc_key, "iv": iv, "tag": tag, "ciphertext": ciphertext}
            plaintext = hybrid_rsa.hybrid_decrypt(priv, container)

            save_path, _ = QFileDialog.getSaveFileName(self, "Сохранить расшифрованный файл как...",
                                                       self._file_name or "decrypted.bin")
            if save_path:
                with open(save_path, "wb") as out:
                    out.write(plaintext)
                self.write_log(f"Файл расшифрован и сохранён: {save_path}")
                QMessageBox.information(self, "OK", f"Файл расшифрован и сохранён: {save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка дешифрования:\n{e}")
