import PyInstaller.__main__
from settings import set_version_app
import os
import datetime
import platform
import shutil
from PIL import Image
import io
import sys
import traceback
import subprocess
import json
from pathlib import Path

def log_exception(exc_type, exc_value, exc_traceback):
    """Логирование необработанных исключений"""
    with open('error.log', 'a') as f:
        f.write(f"Uncaught exception: {exc_type.__name__}: {exc_value}\n")
        f.write(''.join(traceback.format_tb(exc_traceback)))
        f.write('\n')

def prepare_icons(is_mac):
    """Подготовка иконок для разных систем"""
    icon_path = 'icon512.ico'
    if is_mac:
        # Создаем временную директорию для иконок
        iconset_path = 'icon.iconset'
        if os.path.exists(iconset_path):
            shutil.rmtree(iconset_path)
        os.makedirs(iconset_path)

        # Открываем ICO файл
        img = Image.open(icon_path)

        # Создаем иконки разных размеров
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        for size in sizes:
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(f'{iconset_path}/icon_{size}x{size}.png')
            if size <= 512:  # Для @2x
                resized.save(f'{iconset_path}/icon_{size//2}x{size//2}@2x.png')

        # Конвертируем в .icns
        os.system(f'iconutil -c icns {iconset_path}')
        return 'icon.icns', iconset_path
    return icon_path, None

def get_pyinstaller_args(is_mac, is_windows, build_path, icon_path):
    """Получение аргументов для PyInstaller в зависимости от системы"""
    # Определяем разделитель в зависимости от ОС
    separator = ';' if is_windows else ':'

    # Базовые параметры для PyInstaller
    args = [
        'main.py',
        '--onefile',
        '--windowed',
        '--name=dgc',
        f'--icon={icon_path}',
        f'--distpath={build_path}',
        # Добавляем все ресурсы
        f'--add-data=resources/styles/BooleanWidget.qss{separator}resources/styles',
        f'--add-data=resources/styles/ButtonToolBar.qss{separator}resources/styles',
        f'--add-data=resources/styles/ButtonToolBarStatus.qss{separator}resources/styles',
        f'--add-data=resources/styles/CheckBoxWidget.qss{separator}resources/styles',
        f'--add-data=resources/styles/common.qss{separator}resources/styles',
        f'--add-data=resources/styles/ContentForm.qss{separator}resources/styles',
        f'--add-data=resources/styles/MainForm.qss{separator}resources/styles',
        f'--add-data=resources/styles/NumberWidget.qss{separator}resources/styles',
        f'--add-data=resources/styles/SelectWidget.qss{separator}resources/styles',
        f'--add-data=resources/styles/SplashScreen.qss{separator}resources/styles',
        f'--add-data=resources/styles/SettingsForm.qss{separator}resources/styles',
        f'--add-data=resources/styles/SQLWidget.qss{separator}resources/styles',
        f'--add-data=resources/styles/TagInputWidget.qss{separator}resources/styles',
        f'--add-data=resources/styles/TextWidget.qss{separator}resources/styles',
        f'--add-data=resources/styles/ViewTextWidget.qss{separator}resources/styles',
        f'--add-data=resources/images/icon512.ico{separator}resources/images',
        f'--add-data=resources/images/icon512.png{separator}resources/images',
        # Добавляем иконки для кнопок
        f'--add-data=resources/icons/clear.png{separator}resources/icons',
        f'--add-data=resources/icons/plus.png{separator}resources/icons',
        f'--add-data=resources/icons/x.png{separator}resources/icons',
        f'--add-data=resources/icons/save.png{separator}resources/icons',
        f'--add-data=resources/icons/load.png{separator}resources/icons',
        f'--add-data=resources/icons/search.png{separator}resources/icons',
        f'--add-data=resources/icons/gear.png{separator}resources/icons',
        f'--add-data=resources/icons/git.png{separator}resources/icons',
        f'--add-data=resources/icons/load_table.png{separator}resources/icons',
        f'--add-data=resources/icons/load_item.png{separator}resources/icons',
        '--clean',
        '--noconfirm',
        f'--add-data=config{separator}config',
        f'--add-data=template{separator}template',
        f'--add-data=resources{separator}resources',
        f'--add-data=icon512.ico{separator}.',
        # Добавляем все необходимые импорты
        '--hidden-import=PyQt5',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=PyQt5.sip',
        '--hidden-import=psycopg2',
        '--hidden-import=json',
        '--hidden-import=datetime',
        '--hidden-import=pathlib',
        '--hidden-import=os',
        '--hidden-import=settings',
        '--hidden-import=ui.forms.MainForm',
        '--hidden-import=ui.forms.ContentForm',
        '--hidden-import=ui.forms.SettingsForm',
        '--hidden-import=ui.forms.GitForm',
        '--hidden-import=ui.widgets.ActionsConnectWidget',
        '--hidden-import=ui.widgets.CheckBoxWidget',
        '--hidden-import=ui.widgets.ItemTableWidgets',
        '--hidden-import=ui.widgets.LoadingWidget',
        '--hidden-import=ui.widgets.NotificationWidget',
        '--hidden-import=ui.widgets.NumberWidget',
        '--hidden-import=ui.widgets.PageWidget',
        '--hidden-import=ui.widgets.PopoverWidget',
        '--hidden-import=ui.widgets.SQLClickHouseWidget',
        '--hidden-import=ui.widgets.SQLPostgreWidget',
        '--hidden-import=ui.widgets.SelectWidget',
        '--hidden-import=ui.widgets.SQLViewerScript',
        '--hidden-import=ui.widgets.TagInputWidget',
        '--hidden-import=ui.widgets.TextWidget',
        # Собираем все файлы PyQt5
        '--collect-all=PyQt5',
        # Добавляем отладочную информацию
        '--debug=all',
        # Исключаем файлы и модули
        '--exclude-module=_tmp',
        '--exclude-module=.qt_ui',
        '--exclude-module=.vscode',
        '--exclude-module=test',
        '--exclude-module=test2',
    ]

    # Добавляем специфичные параметры для macOS
    if is_mac:
        # Определяем архитектуру системы
        arch = subprocess.check_output(['uname', '-m']).decode().strip()
        target_arch = 'arm64' if arch == 'arm64' else 'x86_64'
        args.extend([
            f'--target-architecture={target_arch}',
            '--osx-bundle-identifier=com.brdpro.dgc',
            '--codesign-identity=-',  # Отключаем подпись для разработки
            '--osx-entitlements-file=entitlements.plist',  # Добавляем файл с правами доступа
        ])

    return args

def build_app():
    """Основная функция сборки приложения"""
    # Устанавливаем обработчик необработанных исключений
    sys.excepthook = log_exception

    # Определяем параметры в зависимости от операционной системы
    is_mac = platform.system() == 'Darwin'
    is_windows = platform.system() == 'Windows'
    build_path = os.path.join('build', 'mac' if is_mac else 'win')

    # Устанавливаем версию приложения
    version_app_short = set_version_app()

    # Сохраняем информацию о версии в JSON файл
    version_info = {
        'version': version_app_short,
        'build_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'build_platform': platform.system(),
        'build_arch': platform.machine()
    }

    # Создаем директорию для ресурсов, если её нет
    os.makedirs('resources', exist_ok=True)

    # Сохраняем информацию о версии
    with open('resources/version.json', 'w') as f:
        json.dump(version_info, f, indent=4)

    # Очищаем директорию сборки
    if os.path.exists(build_path):
        shutil.rmtree(build_path)

    # Подготавливаем иконки
    icon_path, iconset_path = prepare_icons(is_mac)

    # Получаем аргументы для PyInstaller
    pyinstaller_args = get_pyinstaller_args(is_mac, is_windows, build_path, icon_path)

    # Запускаем сборку
    PyInstaller.__main__.run(pyinstaller_args)

    # Очищаем временные файлы
    if is_mac:
        if iconset_path and os.path.exists(iconset_path):
            shutil.rmtree(iconset_path)
        if os.path.exists('icon.icns'):
            os.remove('icon.icns')
        # Копируем файл с логами в директорию сборки
        if os.path.exists('error.log'):
            shutil.copy('error.log', os.path.join(build_path, 'dgc.app', 'Contents', 'MacOS', 'error.log'))

    # Выводим информацию о сборке
    print(f"\nСборка завершена. Приложение находится в директории: {build_path}")
    print(f"Версия приложения: {version_app_short}")
    if is_mac:
        print("\nДля запуска приложения из терминала:")
        print(f"cd {build_path}/dgc.app/Contents/MacOS")
        print("./dgc")
        print("\nДля просмотра логов:")
        print(f"cat {build_path}/dgc.app/Contents/MacOS/error.log")
    elif is_windows:
        print("\nДля запуска приложения:")
        print(f"{build_path}\\dgc.exe")
        print("\nДля просмотра логов:")
        print(f"type {build_path}\\error.log")

if __name__ == "__main__":
    build_app()
