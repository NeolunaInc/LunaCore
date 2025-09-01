import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class KMSStub:
    """Stub KMS for basic AES-256 encryption/decryption."""

    def __init__(self, key: bytes | None = None):
        if key is None:
            key = Fernet.generate_key()
        self.key = key
        self.fernet = Fernet(key)

    def encrypt(self, data: str | bytes) -> str:
        """Encrypt data and return base64 encoded string."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        encrypted = self.fernet.encrypt(data)
        return base64.b64encode(encrypted).decode("utf-8")

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded data and return string."""
        encrypted = base64.b64decode(encrypted_data)
        decrypted = self.fernet.decrypt(encrypted)
        return decrypted.decode("utf-8")

    @staticmethod
    def generate_key(password: str, salt: bytes | None = None) -> bytes:
        """Generate a key from password using PBKDF2."""
        if salt is None:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
