# Standard Library
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
import re
from typing import Optional

from src.config import settings
from src.core.enroll_service import FingerEnrollService
from src.core.identify_service import IdentifyService
from src.core.status import SensorStatus
from src.utils.encrypt import Encrypt
from src.utils.logger import setup_logger

logger = setup_logger("FingerprintManager")
encryptor = Encrypt()

USER_ID_RE = re.compile(r"^[a-zA-Z0-9_\-]+$")


# -------------------------------------------------------------------
# Custom Exceptions
# -------------------------------------------------------------------
class FingerprintError(Exception):
    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code
        super().__init__(message)

    def __repr__(self):
        return f"<FingerprintError {self.code}: {self.message}>"


# -------------------------------------------------------------------
# Utility Functions
# -------------------------------------------------------------------
def _ensure_path(path: Path):
    """Make sure parent directories exist."""
    path.parent.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def _fingerprint_service(service_cls):
    """Async context manager for safe use of fingerprint services."""
    service = None
    try:
        service = service_cls()
        yield service
    finally:
        if service:
            try:
                await asyncio.to_thread(service.close)
            except Exception:
                logger.exception("Error closing fingerprint service (ignored).")


# -------------------------------------------------------------------
# 1. Check Sensor Connection
# -------------------------------------------------------------------
async def check_sensor():
    """
    Check if the fingerprint sensor is connected and responding.
    """
    try:
        async with _fingerprint_service(FingerEnrollService) as service:
            templates = await asyncio.to_thread(service._sensor.read_templates)
            connected = templates is not None
            info = await asyncio.to_thread(service.get_sensor_info) if connected else None
            return {"status": "ok" if connected else "error", "sensor": info}
    except Exception as e:
        logger.exception("Sensor status check failed: %s", e)
        raise FingerprintError("Sensor not connected", 503)


# -------------------------------------------------------------------
# 2. Capture fingerprint and encrypt it
# -------------------------------------------------------------------
async def enroll_fingerprint(user_id: str):
    """
    Capture fingerprint from sensor and return encrypted data.
    File saved at `encrypted/user_<id>.bin`
    """
    if not USER_ID_RE.match(user_id):
        raise FingerprintError("Invalid user_id format", 400)

    filepath = Path(settings.ENCRYPTED_PATH) / f"user_{user_id}.bin"
    _ensure_path(filepath)

    try:
        async with _fingerprint_service(FingerEnrollService) as service:
            result = await asyncio.to_thread(service.enroll_finger)

            status = result.get("status")
            if status != SensorStatus.SUCCESS:
                msg = result.get("message") or status
                logger.warning("Enrollment failed for user %s: %s", user_id, msg)
                raise FingerprintError(f"Enrollment failed: {msg}", 400)

            fingerprint_data = result.get("data")
            if not fingerprint_data:
                raise FingerprintError("No fingerprint data returned from sensor", 500)

            fingerprint_bytes = bytes(fingerprint_data)
            await asyncio.to_thread(
                encryptor.encrypt_to_file,
                filepath,
                fingerprint_bytes,
                settings.SECRET_KEY,
            )

            logger.info("Encrypted fingerprint saved for user %s at %s", user_id, str(filepath))
            return {
                "status": "ok",
                "user_id": user_id,
                "encrypted_path": str(filepath.name),
            }
    except FingerprintError:
        raise
    except Exception as e:
        logger.exception("Enroll failed: %s", e)
        raise FingerprintError("Internal server error during enrollment", 500)


# -------------------------------------------------------------------
# 3. Authenticate user by encrypted fingerprint
# -------------------------------------------------------------------
async def authenticate_with_encrypted(
    user_id: Optional[str] = None,
    file_path: Optional[str] = None,
):
    """
    Authenticate fingerprint using encrypted file.
    Provide either:
      - user_id (for server-stored file)
      - OR file_path (path to encrypted file)
    """
    if not (user_id or file_path):
        raise FingerprintError("Provide either user_id or file_path", 400)

    try:
        # --- Load Encrypted Data ---
        if user_id:
            if not USER_ID_RE.match(user_id):
                raise FingerprintError("Invalid user_id format", 400)
            file_path = Path(settings.ENCRYPTED_PATH) / f"user_{user_id}.bin"
        else:
            file_path = Path(file_path)

        if not file_path.exists():
            raise FingerprintError("Encrypted fingerprint file not found", 404)

        decrypted_data = await asyncio.to_thread(encryptor.decrypt_from_file, file_path, settings.SECRET_KEY)
        if not decrypted_data:
            raise FingerprintError("Decryption failed or file invalid", 500)

        # --- Upload + Authenticate ---
        async with _fingerprint_service(IdentifyService) as identify:
            result = await asyncio.to_thread(identify.upload_to_sensor, decrypted_data)

            if result.get("status") != SensorStatus.SUCCESS:
                raise FingerprintError(f"Failed to upload fingerprint: {result.get('message')}", 400)

            auth_result = await asyncio.to_thread(identify.authenticate)
            if auth_result.get("status") == SensorStatus.SUCCESS:
                return {"status": "ok", "matched_id": auth_result.get("loc_id")}
            if auth_result.get("status") == SensorStatus.NOT_FOUND:
                return {"status": "not found"}
            else:
                return {"status": "failed", "reason": auth_result.get("message")}

    except FingerprintError:
        raise
    except Exception as e:
        logger.exception("Authentication failed: %s", e)
        raise FingerprintError("Internal server error during authentication", 500)


# -------------------------------------------------------------------
# 4. Empty library in sensor memory
# -------------------------------------------------------------------
async def reset_sensor():
    """Clear all stored templates from sensor memory."""
    try:
        async with _fingerprint_service(FingerEnrollService) as service:
            success = await asyncio.to_thread(service.clear_library)
            info = await asyncio.to_thread(service.get_sensor_info)
            return {"status": "ok" if success else "failed", "sensor": info}
    except Exception as e:
        logger.exception("Sensor reset failed: %s", e)
        raise FingerprintError("Failed to reset sensor", 500)
