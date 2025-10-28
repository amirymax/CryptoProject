import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget
from cryptodesk.tabs.caesar_tab import CaesarTab
from cryptodesk.tabs.freq_tab import FreqAnalysisTab
from cryptodesk.tabs.files_tab import FilesTab
from cryptodesk.tabs.hash_tab import HashTab
from cryptodesk.tabs.primes_tab import PrimesTab
from cryptodesk.tabs.classic_tab import ClassicTab
from cryptodesk.tabs.link_tab import LinkTab
from cryptodesk.tabs.docs_tab import DocsTab

class MainWindow(QMainWindow):
    """Главное окно CryptoDesk"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptoDesk")

        tabs = QTabWidget()
        tabs.addTab(CaesarTab(), "Шифр Цезаря")
        tabs.addTab(FreqAnalysisTab(), "Частотный анализ")
        tabs.addTab(FilesTab(), "Файлы")
        tabs.addTab(HashTab(), "Хэширование и подписи")
        tabs.addTab(PrimesTab(), "Простые числа")
        tabs.addTab(ClassicTab(), "Классические шифры")
        tabs.addTab(LinkTab(), "Привязка к Telegram")
        tabs.addTab(DocsTab(), "Документы в БД")
        
        self.setCentralWidget(tabs)
        self.resize(1200, 750)


def main():
    app = QApplication(sys.argv)
    # Подключаем стиль
    with open("cryptodesk/qss/style.qss", "r") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
