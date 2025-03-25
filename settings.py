import os
import json
import platform
import sys
from datetime import datetime

NAME_APP = "DWH Generator Config"
VERSION_APP = "1"
AUTHOR_APP = "BRD Pro"
DESCRIPTION_APP = "DWH Generator Config"
LICENSE_APP = "MIT"
COPYRIGHT_APP = "Copyright 2024 BRD Pro"


def set_version_app():
    """Установка версии приложения в формате MAJOR.YY.MM.DD"""
    global VERSION_APP
    now = datetime.now()
    day_of_year = now.strftime('%j')
    month_of_year = now.strftime('%m')
    year_of_year = now.strftime('%y')

    VERSION_APP = f"{VERSION_APP}.{year_of_year}.{day_of_year}"
    return VERSION_APP

def create_version_file(base_path):
    """Создание файла с информацией о версии"""
    # Устанавливаем текущую версию
    version_app = set_version_app()

    # Формируем информацию о версии
    version_info = {
        'version': version_app,
        'build_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'build_platform': platform.system(),
        'build_arch': platform.machine()
    }

    # Создаем директорию resources, если её нет
    resources_dir = os.path.join(base_path, 'resources')
    os.makedirs(resources_dir, exist_ok=True)

    # Сохраняем информацию о версии
    version_file = os.path.join(resources_dir, 'version.json')
    with open(version_file, 'w') as f:
        json.dump(version_info, f, indent=4)

    return version_info

def get_version_info():
    """Получение информации о версии из JSON файла"""
    try:
        # Получаем путь к файлу version.json
        if getattr(sys, 'frozen', False):
            # Если приложение собрано с PyInstaller
            base_path = sys._MEIPASS
        else:
            # Если приложение запущено из исходного кода
            base_path = os.path.dirname(os.path.abspath(__file__))

        version_file = os.path.join(base_path, 'resources', 'version.json')

        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                return json.load(f)
        elif not getattr(sys, 'frozen', False):
            # Если файл не существует и приложение запущено из исходного кода,
            # создаем его
            return create_version_file(base_path)

    except Exception as e:
        print(f"Ошибка при чтении версии: {e}")

    # Возвращаем значения по умолчанию, если произошла ошибка
    return {
        'version': VERSION_APP,
        'build_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'build_platform': platform.system(),
        'build_arch': platform.machine()
    }

if __name__ == "__main__":
    print(set_version_app())