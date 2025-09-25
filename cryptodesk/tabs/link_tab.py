import platform
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QMessageBox
)


class LinkTab(QWidget):
    """
    Вкладка: Привязка к Telegram (через одноразовый код).
    """
    API_URL = "http://localhost:8000/link/verify"  # адрес FastAPI

    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        # Поле для ввода кода
        self.layout().addWidget(QLabel("Введите код, полученный в Telegram-боте:"))
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Например: 1234")
        self.layout().addWidget(self.code_input)

        # Кнопка проверки
        self.verify_btn = QPushButton("Проверить код")
        self.layout().addWidget(self.verify_btn)

        # Лог
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.layout().addWidget(QLabel("Результаты:"))
        self.layout().addWidget(self.log)

        # Сигналы
        self.verify_btn.clicked.connect(self.on_verify)

    def write_log(self, text: str):
        self.log.append(text)
        self.log.ensureCursorVisible()

    def on_verify(self):
        code = self.code_input.text().strip()
        if not code.isdigit():
            QMessageBox.warning(self, "Ошибка", "Код должен состоять из цифр.")
            return

        try:
            # Определяем имя компьютера
            device_name = platform.node()

            # Отправляем запрос к API
            resp = requests.post(
                self.API_URL,
                json={"code": code,
                      "device_name": device_name},
                timeout=5
            )

            if resp.status_code == 200:
                data = resp.json()
                self.write_log(f"✅ Привязка успешна: {data}")
                QMessageBox.information(self, "OK", f"Привязка успешна ✅\nКомпьютер: {device_name}")
            else:
                self.write_log(f"❌ Ошибка: {resp.text}")
                QMessageBox.warning(self, "Ошибка", f"Код не принят ❌\n{resp.text}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при подключении:\n{e}")
