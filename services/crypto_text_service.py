import base64
import getpass
from cryptography.fernet import Fernet

from services.logger_service import LoggerService


class CryptoTextService:
    def __init__(self,
                 logger_service: LoggerService=None):
        """
        Инициализация сервиса шифрования текста.
        """
        self.logger_service = logger_service
        self.salt = None
        self.key = None
        self.init_config()


    def init_config(self):
        self.salt = getpass.getuser()
        self.key = base64.urlsafe_b64encode(self.salt.encode('utf-8')[:32].ljust(32, b'\0'))


    def set_crypto_pass(self, password: str) -> str:
        """
        Шифрует пароль с использованием Fernet.
        """
        f = Fernet(self.key)
        encrypted_password = f.encrypt(password.encode('utf-8'))
        return base64.b64encode(encrypted_password).decode('utf-8')

    def get_crypto_pass(self, hashed_password: str) -> str:
        """
        Расшифровывает пароль с использованием Fernet.
        """
        try:
            f = Fernet(self.key)
            decrypted_password = f.decrypt(base64.b64decode(hashed_password.encode('utf-8')))
            return decrypted_password.decode('utf-8')
        except Exception as e:
            if self.logger_service is not None:
                self.logger_service.error(f"Ошибка при расшифровке пароля: {str(e)}")
            # raise ValueError(f"Ошибка при расшифровке пароля: {str(e)}")
            return ""
if __name__ == "__main__":
    crypto_text_service = CryptoTextService()
    hashed_password = crypto_text_service.set_crypto_pass("123456")
    print(hashed_password)
    print(crypto_text_service.get_crypto_pass(hashed_password))
