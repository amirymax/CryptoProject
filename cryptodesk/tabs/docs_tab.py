import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QFileDialog, QMessageBox
)


class DocsTab(QWidget):
    """
    Вкладка: Документы в БД (работа через API).
    """
    API_URL = "http://localhost:8000/documents"

    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        # Кнопки
        self.upload_btn = QPushButton("📂 Загрузить документ в БД")
        self.list_btn = QPushButton("📋 Показать список документов")
        self.layout().addWidget(self.upload_btn)
        self.layout().addWidget(self.list_btn)

        # Лог
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.layout().addWidget(QLabel("Результаты:"))
        self.layout().addWidget(self.log)

        # Сигналы
        self.upload_btn.clicked.connect(self.upload_document)
        self.list_btn.clicked.connect(self.list_documents)

    def write_log(self, text: str):
        self.log.append(text)
        self.log.ensureCursorVisible()

    def upload_document(self):
        """Загрузить файл в БД"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if not file_path:
            return

        try:
            # Читаем бинарные данные
            with open(file_path, "rb") as f:
                data = f.read()

            payload = {
                "filename": file_path.split("/")[-1],
                "encrypted_data": data.hex(),  # 👈 передаём как hex
                "cipher_meta": {"method": "demo-aes"}
            }

            resp = requests.post(f"{self.API_URL}/upload", json=payload)
            if resp.status_code == 200:
                self.write_log(f"✅ Загружено: {resp.json()}")
            else:
                self.write_log(f"❌ Ошибка: {resp.text}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить документ:\n{e}")

    def list_documents(self):
        """Получить список документов"""
        try:
            resp = requests.get(f"{self.API_URL}/list")
            if resp.status_code == 200:
                docs = resp.json()
                self.write_log("📋 Документы в БД:")
                for d in docs:
                    self.write_log(f" - {d['id']} | {d['filename']} | {d['created_at']}")
            else:
                self.write_log(f"❌ Ошибка: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить список:\n{e}")
