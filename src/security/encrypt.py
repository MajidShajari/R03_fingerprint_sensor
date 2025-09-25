import os
from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from src.utils.logger import setup_logger

local_logger = setup_logger("Encrypt")


class Encrypt:
    def __init__(self, iterations: int = 390000):
        self.iterations = iterations
        self.backend = default_backend()

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 key
            salt=salt,
            iterations=self.iterations,
            backend=self.backend,
        )
        return kdf.derive(password.encode())

    def _encrypt(self, data: bytes, password: str) -> tuple[bytes, bytes, bytes]:
        if not isinstance(data, bytes):
            data = bytes(data)
        salt = os.urandom(16)
        key = self._derive_key(password, salt)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, data, None)
        return ct, nonce, salt

    def _decrypt(self, ct: bytes, nonce: bytes, salt: bytes, password: str) -> bytes:
        key = self._derive_key(password, salt)
        aesgcm = AESGCM(key)
        local_logger.info("Decrypting data...")
        return list(aesgcm.decrypt(nonce, ct, None))

    def encrypt_to_file(self, filepath: Path, data: bytes, password: str):
        ct, nonce, salt = self._encrypt(data, password)
        with open(filepath, "wb") as f:
            f.write(salt + nonce + ct)
        local_logger.info("Data encrypted and saved to : %s", filepath)
        return True

    def decrypt_from_file(self, filepath: Path, password: str) -> bytes:
        with open(filepath, "rb") as f:
            raw = f.read()
        salt, nonce, ct = raw[:16], raw[16:28], raw[28:]
        local_logger.info("Data read from %s, starting decryption", filepath)
        return self._decrypt(ct, nonce, salt, password)
