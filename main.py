import time

from src.config import LED,ENCRYPTED_PATH,DECRYPTED_PATH
from src.core.enroll import Enroll
from src.core.identify import Identify
from src.security.encrypt import Encrypt
from src.core.status import SensorStatus
from src.utils.setup_paths import ensure_paths

ensure_paths()


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


enroller = Enroll(on_status=feedback)
enroller.config_led(LED["ready"])
data = enroller.get_raw()
time.sleep(2)
if data and isinstance(data, list):
    enroller.config_led(LED["succes"])
    print(f"Enrolled successfully")
    time.sleep(2)
else:
    enroller.config_led(LED["error"])
    time.sleep(2)
    raise SystemExit("Enrollment Failed")
enroller.close()
encrypter = Encrypt()
file_path = ENCRYPTED_PATH/"4433509132.bin"
encrypted_data = encrypter.encrypt_to_file(file_path,data,"11235813")
if not encrypted_data:
    raise SystemExit("Encryption Failed")
decrypted_data = encrypter.decrypt_from_file(file_path,"11235813")
if not decrypted_data:
    raise SystemExit("Decryption Failed")
identifier = Identify(on_status=feedback)
identifier.config_led(LED["ready"])
status = identifier.upload_to_sensor(decrypted_data)
if status[0] == SensorStatus.SUCCESS:
    print(f"Uploaded successfully in :{status[1]}")
    identifier.config_led(LED["succes"])
    time.sleep(2)
else:
    identifier.config_led(LED["error"])
    time.sleep(2)
    raise SystemExit("Upload Failed")
identifier.config_led(LED["process"])
time.sleep(2)
status = identifier.authenticate()
if status[0] == SensorStatus.SUCCESS:
    print(f"Authenticated ID: {status[1]}")
    identifier.config_led(LED["succes"])
    time.sleep(2)
else:
    identifier.config_led(LED["error"])
    time.sleep(2)
identifier.close()
