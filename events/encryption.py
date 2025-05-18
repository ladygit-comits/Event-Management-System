from cryptography.fernet import Fernet
from django.conf import settings
import base64
import hashlib

# Generate a key using part of the SECRET_KEY (must be 32 bytes for Fernet)
key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
fernet = Fernet(base64.urlsafe_b64encode(key))

def encrypt_data(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
