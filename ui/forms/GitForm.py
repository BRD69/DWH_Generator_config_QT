from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QMessageBox,
                             QFileDialog, QGroupBox, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
import git
import json
import os

class GitForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.repo = None
        self._setup_ui()

    def _setup_ui(self):
        """Инициализация пользовательского интерфейса"""
        layout = QVBoxLayout()

        # Группа для подключения к репозиторию
        repo_group = QGroupBox("Подключение к репозиторию")
        repo_layout = QVBoxLayout()

        # Поле для пути к репозиторию
        repo_path_layout = QHBoxLayout()
        self.repo_path = QLineEdit()
        self.repo_path.setPlaceholderText("Путь к репозиторию")
        browse_btn = QPushButton("Обзор")
        browse_btn.clicked.connect(self.browse_repo)
        repo_path_layout.addWidget(QLabel("Путь:"))
        repo_path_layout.addWidget(self.repo_path)
        repo_path_layout.addWidget(browse_btn)

        # Кнопки для работы с репозиторием
        repo_buttons_layout = QHBoxLayout()
        repo_buttons_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding))
        self.connect_btn = QPushButton("Подключиться")
        self.connect_btn.clicked.connect(self.connect_repo)
        self.disconnect_btn = QPushButton("Отключиться")
        self.disconnect_btn.clicked.connect(self.disconnect_repo)
        self.disconnect_btn.setEnabled(False)
        repo_buttons_layout.addWidget(self.connect_btn)
        repo_buttons_layout.addWidget(self.disconnect_btn)

        repo_layout.addLayout(repo_path_layout)
        repo_layout.addLayout(repo_buttons_layout)
        repo_group.setLayout(repo_layout)

        # Группа для работы с файлами
        files_group = QGroupBox("Работа с файлами")
        files_layout = QVBoxLayout()

        # Поле для пути к файлу
        file_path_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText("Путь к файлу")
        file_browse_btn = QPushButton("Обзор")
        file_browse_btn.clicked.connect(self.browse_file)
        file_path_layout.addWidget(QLabel("Файл:"))
        file_path_layout.addWidget(self.file_path)
        file_path_layout.addWidget(file_browse_btn)

        # Кнопки для работы с Git
        git_buttons_layout = QHBoxLayout()
        git_buttons_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding))
        self.commit_btn = QPushButton("Коммит")
        self.commit_btn.clicked.connect(self.commit_changes)
        self.commit_btn.setEnabled(False)
        self.push_btn = QPushButton("Пуш")
        self.push_btn.clicked.connect(self.push_changes)
        self.push_btn.setEnabled(False)
        git_buttons_layout.addWidget(self.commit_btn)
        git_buttons_layout.addWidget(self.push_btn)

        files_layout.addLayout(file_path_layout)
        files_layout.addLayout(git_buttons_layout)
        files_group.setLayout(files_layout)

        # Поле для сообщения коммита
        commit_message_layout = QVBoxLayout()
        commit_message_layout.addWidget(QLabel("Сообщение коммита:"))
        self.commit_message = QTextEdit()
        self.commit_message.setMaximumHeight(100)
        commit_message_layout.addWidget(self.commit_message)

        # Добавляем все группы в основной layout
        layout.addWidget(repo_group)
        layout.addWidget(files_group)
        layout.addLayout(commit_message_layout)

        self.setLayout(layout)

    def browse_repo(self):
        """Открывает диалог выбора директории репозитория"""
        dir_path = QFileDialog.getExistingDirectory(self, "Выберите директорию репозитория")
        if dir_path:
            self.repo_path.setText(dir_path)

    def browse_file(self):
        """Открывает диалог выбора файла"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "JSON files (*.json)")
        if file_path:
            self.file_path.setText(file_path)

    def connect_repo(self):
        """Подключается к Git репозиторию"""
        try:
            repo_path = self.repo_path.text()
            if not repo_path:
                QMessageBox.warning(self, "Ошибка", "Укажите путь к репозиторию")
                return

            self.repo = git.Repo(repo_path)
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.commit_btn.setEnabled(True)
            self.push_btn.setEnabled(True)
            QMessageBox.information(self, "Успех", "Успешно подключено к репозиторию")
        except git.InvalidGitRepositoryError:
            QMessageBox.warning(self, "Ошибка", "Указанная директория не является Git репозиторием")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при подключении к репозиторию: {str(e)}")

    def disconnect_repo(self):
        """Отключается от Git репозитория"""
        self.repo = None
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.commit_btn.setEnabled(False)
        self.push_btn.setEnabled(False)
        QMessageBox.information(self, "Успех", "Отключено от репозитория")

    def commit_changes(self):
        """Создает коммит с изменениями"""
        try:
            if not self.repo:
                QMessageBox.warning(self, "Ошибка", "Не подключено к репозиторию")
                return

            file_path = self.file_path.text()
            if not file_path:
                QMessageBox.warning(self, "Ошибка", "Укажите путь к файлу")
                return

            commit_msg = self.commit_message.toPlainText()
            if not commit_msg:
                QMessageBox.warning(self, "Ошибка", "Введите сообщение коммита")
                return

            # Добавляем файл в индекс
            self.repo.index.add([file_path])

            # Создаем коммит
            self.repo.index.commit(commit_msg)

            QMessageBox.information(self, "Успех", "Изменения успешно закоммичены")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при создании коммита: {str(e)}")

    def push_changes(self):
        """Отправляет изменения в удаленный репозиторий"""
        try:
            if not self.repo:
                QMessageBox.warning(self, "Ошибка", "Не подключено к репозиторию")
                return

            # Получаем текущую ветку
            current_branch = self.repo.active_branch

            # Отправляем изменения
            self.repo.remotes.origin.push(current_branch)

            QMessageBox.information(self, "Успех", "Изменения успешно отправлены в репозиторий")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при отправке изменений: {str(e)}")

    def set_json_data(self, json_data: dict):
        """Устанавливает JSON данные для сохранения"""
        try:
            if not self.repo:
                QMessageBox.warning(self, "Ошибка", "Не подключено к репозиторию")
                return

            # Сохраняем JSON в файл
            file_path = os.path.join(self.repo.working_dir, "config.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)

            self.file_path.setText(file_path)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при сохранении JSON: {str(e)}")

    def show(self):
        """Переопределяем метод show для установки размеров окна"""
        super().show()
        self.resize(800, 600)