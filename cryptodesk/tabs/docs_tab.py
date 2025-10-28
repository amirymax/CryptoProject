import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QFileDialog, 
    QMessageBox, QSizePolicy, QGridLayout, QProgressDialog, QApplication
)

from datetime import datetime
from PySide6.QtCore import Qt


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
            no_encrypted_data = resp.json()
            del no_encrypted_data['encrypted_data']  # 👈 удаляем из лога
            if resp.status_code == 200:
                self.write_log(f"✅ Загружено: {no_encrypted_data}")
            else:
                self.write_log(f"❌ Ошибка: {resp.text}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить документ:\n{e}")

    def list_documents(self):
        """Показать список документов в виде таблицы с заголовками колонок"""

        try:
            resp = requests.get(f"{self.API_URL}/list")
            if resp.status_code != 200:
                self.write_log(f"❌ Ошибка: {resp.text}")
                return

            docs = resp.json()
            self.log.clear()

            if not hasattr(self, "docs_table_container"):
                # Контейнер таблицы (создаём один раз)
                self.docs_table_container = QWidget()
                self.docs_grid = QGridLayout(self.docs_table_container)
                self.docs_grid.setContentsMargins(0, 8, 0, 0)
                self.docs_grid.setHorizontalSpacing(12)
                self.docs_grid.setVerticalSpacing(8)
                # Таблица тянется, колонки выравниваются
                self.docs_grid.setColumnStretch(0, 4)  # Имя — широкая
                self.docs_grid.setColumnStretch(1, 2)  # Дата
                self.docs_grid.setColumnStretch(2, 1)  # ID
                self.docs_grid.setColumnStretch(3, 0)  # Скачать
                self.docs_grid.setColumnStretch(4, 0)  # Удалить
                self.layout().addWidget(self.docs_table_container)

            # Очистим прежние строки таблицы
            while self.docs_grid.count():
                item = self.docs_grid.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()

            # Если пусто — покажем сообщение и выйдем
            if not docs:
                self.write_log("📂 В базе данных пока нет документов.")
                return

            self.write_log("📂 Документы в БД:\n")

            # ===== ШАПКА ТАБЛИЦЫ =====
            def header(text, align=Qt.AlignLeft):
                lbl = QLabel(text)
                lbl.setStyleSheet("color:#dfe8ff; font-weight:600;")
                lbl.setAlignment(align | Qt.AlignVCenter)
                return lbl

            self.docs_grid.addWidget(header("Имя файла"),         0, 0)
            self.docs_grid.addWidget(header("Дата"),               0, 1, alignment=Qt.AlignCenter)
            self.docs_grid.addWidget(header("ID"),                 0, 2, alignment=Qt.AlignCenter)
            self.docs_grid.addWidget(header("Действия", Qt.AlignCenter), 0, 3, 1, 2)

            # ===== СТРОКИ ДОКУМЕНТОВ =====
            for row_idx, d in enumerate(docs, start=1):
                doc_id = d["id"]
                filename = d["filename"]
                created = d["created_at"]

                # Имя без путей
                name = filename.split("/")[-1].split("\\")[-1]
                # Дата → 02.10.2025  01:15
                try:
                    date_str = datetime.fromisoformat(created.replace("Z", "")).strftime("%d.%m.%Y  %H:%M")
                except Exception:
                    date_str = created

                # Ячейки
                name_lbl = QLabel(name)
                name_lbl.setStyleSheet("color:#cfd4e0;")
                name_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

                date_lbl = QLabel(date_str)
                date_lbl.setAlignment(Qt.AlignCenter)
                date_lbl.setStyleSheet("color:#cfd4e0;")

                id_lbl = QLabel(str(doc_id))
                id_lbl.setAlignment(Qt.AlignCenter)
                id_lbl.setStyleSheet("color:#aab3c2;")

                btn_download = QPushButton("📥 Скачать")
                btn_download.setFixedWidth(110)
                btn_download.clicked.connect(lambda _, _id=doc_id: self.download_document(_id))

                btn_delete = QPushButton("🗑 Удалить")
                btn_delete.setFixedWidth(110)
                btn_delete.clicked.connect(lambda _, _id=doc_id: self.delete_document(_id, None))

                # Добавляем в сетку
                self.docs_grid.addWidget(name_lbl,     row_idx, 0)
                self.docs_grid.addWidget(date_lbl,     row_idx, 1)
                self.docs_grid.addWidget(id_lbl,       row_idx, 2)
                self.docs_grid.addWidget(btn_download, row_idx, 3, alignment=Qt.AlignRight)
                self.docs_grid.addWidget(btn_delete,   row_idx, 4, alignment=Qt.AlignRight)

        except Exception as e:
            self.write_log(f"❌ Не удалось получить список:\n{e}")



    def download_document(self, doc_id: int):
        """Скачать документ и сохранить на диск"""
        try:
            resp = requests.get(f"{self.API_URL}/{doc_id}")
            if resp.status_code != 200:
                self.write_log(f"❌ Ошибка API: {resp.text}")
                return

            doc = resp.json()
            filename = doc["filename"]
            data = bytes.fromhex(doc["encrypted_data"])

            # Выбор куда сохранить
            from PySide6.QtWidgets import QFileDialog
            save_path, _ = QFileDialog.getSaveFileName(self, "Сохранить как", filename)
            if not save_path:
                return

            with open(save_path, "wb") as f:
                f.write(data)

            self.write_log(f"✅ Файл сохранён: {save_path}")

        except Exception as e:
            self.write_log(f"❌ Ошибка скачивания:\n{e}")

    def delete_document(self, doc_id: int, row_widget=None):

        # Подтверждение
        confirm = QMessageBox.question(
            self,
            "Удалить документ",
            f"Вы уверены, что хотите удалить документ ID {doc_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        # Индикатор загрузки (индетерминативный)
        spinner = QProgressDialog("Удаление документа...", None, 0, 0, self)
        spinner.setWindowModality(Qt.ApplicationModal)
        spinner.setAutoClose(True)
        spinner.setCancelButton(None)
        spinner.setMinimumDuration(0)
        spinner.show()
        QApplication.processEvents()

        try:
            resp = requests.delete(f"{self.API_URL}/{doc_id}", timeout=15)
            if resp.status_code == 200:
                # Успех: либо удаляем конкретную строку, либо обновляем таблицу целиком
                if row_widget is not None:
                    row_widget.setParent(None)
                    row_widget.deleteLater()
                else:
                    # В варианте с QGridLayout строки не имеют собственного контейнера,
                    # поэтому просто перерисуем весь список
                    self.list_documents()
                self.write_log(f"🗑 Документ {doc_id} удалён.")
            else:
                self.write_log(f"❌ Ошибка API при удалении: {resp.status_code} {resp.text}")
        except Exception as e:
            self.write_log(f"❌ Не удалось удалить документ:\n{e}")
        finally:
            spinner.close()

