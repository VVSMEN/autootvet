"""
Security utilities for encrypting/decrypting API keys
"""
from cryptography.fernet import Fernet
from app.core.config import settings


class CryptoService:
    """Service for encrypting and decrypting sensitive data"""

    def __init__(self):
        """Initialize with encryption key from settings"""
        try:
            self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
        except Exception:
            key = Fernet.generate_key()
            self.cipher = Fernet(key)

    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        if not data:
            return ""
        encrypted = self.cipher.encrypt(data.encode())
        return encrypted.decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt encrypted string"""
        if not encrypted_data:
            return ""
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()


crypto_service = CryptoService()
