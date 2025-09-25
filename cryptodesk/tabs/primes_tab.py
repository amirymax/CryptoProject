import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout,
    QLineEdit, QComboBox, QMessageBox
)

from crypto_core.primes import primes


class PrimesTab(QWidget):
    """
    Вкладка для проверки чисел на простоту (Ферма, Миллера–Рабина)
    и генерации случайных простых чисел.
    """

    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        # Поле для ввода числа
        self.input_num = QLineEdit()
        self.input_num.setPlaceholderText("Введите число для проверки...")
        self.layout().addWidget(QLabel("Число:"))
        self.layout().addWidget(self.input_num)

        # Кнопки проверки
        check_row = QHBoxLayout()
        self.ferma_btn = QPushButton("Проверить (Ферма)")
        self.mr_btn = QPushButton("Проверить (Миллер–Рабин)")
        check_row.addWidget(self.ferma_btn)
        check_row.addWidget(self.mr_btn)
        self.layout().addLayout(check_row)

        # Кнопка генерации простого
        gen_row = QHBoxLayout()
        self.bits_box = QComboBox()
        self.bits_box.addItems(["16", "32", "64"])
        self.gen_btn = QPushButton("Сгенерировать простое")
        gen_row.addWidget(QLabel("Биты:"))
        gen_row.addWidget(self.bits_box)
        gen_row.addWidget(self.gen_btn)
        self.layout().addLayout(gen_row)

        # Лог
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.layout().addWidget(QLabel("Результаты:"))
        self.layout().addWidget(self.log)

        # Сигналы
        self.ferma_btn.clicked.connect(self.on_ferma)
        self.mr_btn.clicked.connect(self.on_mr)
        self.gen_btn.clicked.connect(self.on_generate)

    def write_log(self, text: str):
        self.log.append(text)
        self.log.ensureCursorVisible()

    def on_ferma(self):
        num_text = self.input_num.text().strip()
        if not num_text.isdigit():
            QMessageBox.warning(self, "Ошибка", "Введите корректное целое число.")
            return
        n = int(num_text)
        res = primes.is_prime_fermat(n)
        if res:
            self.write_log(f"Ферма: {n} вероятно простое ✅")
        else:
            self.write_log(f"Ферма: {n} составное ❌")

    def on_mr(self):
        num_text = self.input_num.text().strip()
        if not num_text.isdigit():
            QMessageBox.warning(self, "Ошибка", "Введите корректное целое число.")
            return
        n = int(num_text)
        res = primes.is_prime_miller_rabin(n)
        if res:
            self.write_log(f"Миллер–Рабин: {n} вероятно простое ✅")
        else:
            self.write_log(f"Миллер–Рабин: {n} составное ❌")

    def on_generate(self):
        bits = int(self.bits_box.currentText())
        prime = primes.generate_prime(bits)
        self.write_log(f"Сгенерировано {bits}-битное простое число: {prime}")
        self.input_num.setText(str(prime))
