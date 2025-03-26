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

def log_exception(exc_type, exc_value, exc_traceback):
    """Логирование необработанных исключений"""
    with open('error.log', 'a') as f:
        f.write(f"Uncaught exception: {exc_type.__name__}: {exc_value}\n")
        f.write(''.join(traceback.format_tb(exc_traceback)))
        f.write('\n')

# Устанавливаем обработчик необработанных исключений
sys.excepthook = log_exception

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

# Определяем параметры в зависимости от операционной системы
is_mac = platform.system() == 'Darwin'
is_windows = platform.system() == 'Windows'
build_path = os.path.join('build', 'mac' if is_mac else 'win')

# Очищаем директорию сборки
if os.path.exists(build_path):
    shutil.rmtree(build_path)

# Конвертируем иконку для macOS
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
    icon_path = 'icon.icns'

# Базовые параметры для PyInstaller
pyinstaller_args = [
    'main.py',
    '--onefile',
    '--windowed',
    '--name=dwhgenerator',
    f'--icon={icon_path}',
    f'--distpath={build_path}',
    'datas=[("resources/styles/*.qss", "resources/styles"), ("resources/images/*.png", "resources/images"), ("resources/images/*.ico", "resources/images") ]',
    '--clean',
    '--noconfirm',
    '--add-data=config:config',
    '--add-data=template:template',
    '--add-data=resources:resources',
    '--add-data=icon512.ico:.',
    '--hidden-import=PyQt5',
    '--hidden-import=psycopg2',
    '--hidden-import=json',
    '--hidden-import=datetime',
    '--hidden-import=pathlib',
    '--hidden-import=os',
    '--hidden-import=settings',
    '--hidden-import=ui.forms.MainForm',
    '--hidden-import=ui.forms.ViewForm',
    '--hidden-import=ui.widgets.CheckBoxWidget',
    '--hidden-import=ui.widgets.ItemTableWidgets',
    '--hidden-import=ui.widgets.NumberWidget',
    '--hidden-import=ui.widgets.PageWidget',
    '--hidden-import=ui.widgets.SelectWidget',
    '--hidden-import=ui.widgets.TagInputWidget',
    '--hidden-import=ui.widgets.TextWidget',
    # Исключаем файлы и модули
    '--exclude-module=.qt_ui',
    '--exclude-module=.vscode',
    '--exclude-module=tmp',
    '--exclude-module=test',
    '--exclude-module=test2',
]

# Добавляем специфичные параметры для macOS
if is_mac:
    # Определяем архитектуру системы
    arch = subprocess.check_output(['uname', '-m']).decode().strip()
    target_arch = 'arm64' if arch == 'arm64' else 'x86_64'

    pyinstaller_args.extend([
        f'--target-architecture={target_arch}',
        '--osx-bundle-identifier=com.brdpro.dwhgenerator',
        '--codesign-identity=-',  # Отключаем подпись для разработки
        '--debug=all',  # Включаем отладочную информацию
        '--osx-entitlements-file=entitlements.plist',  # Добавляем файл с правами доступа
    ])

# Запускаем сборку
PyInstaller.__main__.run(pyinstaller_args)

# Очищаем временные файлы
if is_mac:
    if os.path.exists(iconset_path):
        shutil.rmtree(iconset_path)
    if os.path.exists('icon.icns'):
        os.remove('icon.icns')
    # Копируем файл с логами в директорию сборки
    if os.path.exists('error.log'):
        shutil.copy('error.log', os.path.join(build_path, 'dwhgenerator.app', 'Contents', 'MacOS', 'error.log'))

# Выводим информацию о сборке
print(f"\nСборка завершена. Приложение находится в директории: {build_path}")
print(f"Версия приложения: {version_app_short}")
if is_mac:
    print("\nДля запуска приложения из терминала:")
    print(f"cd {build_path}/dwhgenerator.app/Contents/MacOS")
    print("./dwhgenerator")
    print("\nДля просмотра логов:")
    print(f"cat {build_path}/dwhgenerator.app/Contents/MacOS/error.log")
