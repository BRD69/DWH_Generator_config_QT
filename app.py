import base64
import getpass
from cryptography.fernet import Fernet

def set_crypto_pass(password: str, salt = None) -> str:
    """
    Шифрует пароль с использованием имени пользователя системы как соли.

    Args:
        password (str): Пароль для шифрования

    Returns:
        str: Зашифрованный пароль в формате base64
    """
    # Получаем имя пользователя системы как соль
    if salt is None:
        salt = getpass.getuser()

    # Создаем ключ на основе соли
    key = base64.urlsafe_b64encode(salt.encode('utf-8')[:32].ljust(32, b'\0'))

    # Создаем Fernet для шифрования
    f = Fernet(key)

    # Шифруем пароль
    encrypted_password = f.encrypt(password.encode('utf-8'))
    return base64.b64encode(encrypted_password).decode('utf-8')

def get_crypto_pass(hashed_password: str, salt = None) -> str:
    """
    Расшифровывает пароль, используя имя пользователя системы как соль.

    Args:
        hashed_password (str): Зашифрованный пароль в формате base64

    Returns:
        str: Расшифрованный пароль
    """
    try:
        # Получаем имя пользователя системы как соль
        if salt is None:
            salt = getpass.getuser()

        # Создаем ключ на основе соли
        key = base64.urlsafe_b64encode(salt.encode('utf-8')[:32].ljust(32, b'\0'))

        # Создаем Fernet для расшифровки
        f = Fernet(key)

        # Декодируем зашифрованный пароль из base64
        encrypted_password = base64.b64decode(hashed_password)

        # Расшифровываем пароль
        decrypted_password = f.decrypt(encrypted_password)
        return decrypted_password.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Ошибка при расшифровке пароля: {str(e)}")

if __name__ == "__main__":
    # Пример использования
    password = "test_password"

    # Шифруем пароль
    hashed = set_crypto_pass(password)
    print(f"Зашифрованный пароль: {hashed}")

    # Расшифровываем пароль
    decrypted = get_crypto_pass(hashed)
    print(f"Расшифрованный пароль: {decrypted}")


