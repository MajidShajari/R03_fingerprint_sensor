import time

from core.enroll_service import FingerEnrollService
from core.identify_service import IdentifyService
from src.config import ENCRYPTED_PATH, LED
from src.core.status import SensorStatus
from utils.encrypt import Encrypt


def feedback(status: SensorStatus):
    if status == SensorStatus.PLACE_FINGER:
        print("👉 Place Finger")
    elif status == SensorStatus.REMOVE_FINGER:
        print("✋ Remove Finger")
    elif status == SensorStatus.PLACE_SAME_FINGER:
        print("👉 Place Same Finger Again")
    elif status == SensorStatus.SUCCESS:
        print("✅ Successful")
    elif status == SensorStatus.FAIL:
        print("❌ Enrollment Failed")
    elif status == SensorStatus.STORAGE_FULL:
        print("⚠️ Storage Full")
    elif status == SensorStatus.LOCATION_OCCUPIED:
        print("⚠️ Location Occupied")


enroller = FingerEnrollService(on_status=feedback)
enroller.config_led(LED["ready"])
data = enroller.get_raw()
time.sleep(2)
if data and isinstance(data, list):
    enroller.config_led(LED["succes"])
    print("Enrolled successfully")
    time.sleep(2)
else:
    enroller.config_led(LED["error"])
    time.sleep(2)
    raise SystemExit("Enrollment Failed")
enroller.close()
encrypter = Encrypt()
file_path = ENCRYPTED_PATH / "4433509132.bin"
ENCRYPTED_DATA = encrypter.encrypt_to_file(file_path, data, "11235813")
if not ENCRYPTED_DATA:
    raise SystemExit("Encryption Failed")
DECRYPTED_DATA = encrypter.decrypt_from_file(file_path, "11235813")
if not DECRYPTED_DATA:
    raise SystemExit("Decryption Failed")
identifier = IdentifyService(on_status=feedback)
identifier.config_led(LED["ready"])
_status = identifier.upload_to_sensor(DECRYPTED_DATA)
if _status[0] == SensorStatus.SUCCESS:
    print(f"Uploaded successfully in :{_status[1]}")
    identifier.config_led(LED["succes"])
    time.sleep(2)
else:
    identifier.config_led(LED["error"])
    time.sleep(2)
    raise SystemExit("Upload Failed")
identifier.config_led(LED["process"])
time.sleep(2)
_status = identifier.authenticate()
if _status[0] == SensorStatus.SUCCESS:
    print(f"Authenticated ID: {_status[1]}")
    identifier.config_led(LED["succes"])
    time.sleep(2)
else:
    identifier.config_led(LED["error"])
    time.sleep(2)
identifier.close()
