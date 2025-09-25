from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QTextEdit, QPushButton, QHBoxLayout, QMessageBox
)
from crypto_core.classic import freq_analysis, caesar_breaker


class FreqAnalysisTab(QWidget):
    """Вкладка для частотного анализа и взлома Цезаря"""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Ввод текста
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Введите зашифрованный текст...")
        layout.addWidget(QLabel("Текст для анализа:"))
        layout.addWidget(self.input_text)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.plot_btn = QPushButton("Показать гистограмму")
        self.break_btn = QPushButton("Автовзлом Цезаря")
        btn_layout.addWidget(self.plot_btn)
        btn_layout.addWidget(self.break_btn)
        layout.addLayout(btn_layout)

        # Результат
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(QLabel("Результат:"))
        layout.addWidget(self.result_box)

        self.setLayout(layout)

        # Сигналы
        self.plot_btn.clicked.connect(self.plot_freqs)
        self.break_btn.clicked.connect(self.break_caesar)

    def plot_freqs(self):
        text = self.input_text.toPlainText()
        freqs = freq_analysis.letter_frequencies(text)
        if not freqs:
            QMessageBox.warning(self, "Ошибка", "Нет букв для анализа.")
            return
        freq_analysis.plot_frequencies(freqs, "Частотный анализ")

    def break_caesar(self):
        text = self.input_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Ошибка", "Введите текст для взлома.")
            return
        key, decrypted = caesar_breaker.break_caesar(text)
        self.result_box.setPlainText(
            f"Предположительный ключ: {key}\n\nДешифрованный текст:\n{decrypted}"
        )
