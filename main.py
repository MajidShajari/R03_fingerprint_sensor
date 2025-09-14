import time

from src.config import LED
from src.core.enroll import Enroll
from src.core.identify import Identify
from src.core.status import EnrollStatus, IdentifyStatus
from src.utils.setup_paths import ensure_paths

ensure_paths()


def feedback(status: EnrollStatus):
    if status == EnrollStatus.PLACE_FINGER:
        print("👉 Place Finger")
    elif status == EnrollStatus.REMOVE_FINGER:
        print("✋ Remove Finger")
    elif status == EnrollStatus.PLACE_SAME_FINGER:
        print("👉 Place Same Finger Again")
    elif status == EnrollStatus.SUCCESS:
        print("✅ Enrollment Successful")
    elif status == EnrollStatus.FAIL:
        print("❌ Enrollment Failed")
    elif status == EnrollStatus.STORAGE_FULL:
        print("⚠️ Storage Full")
    elif status == EnrollStatus.LOCATION_OCCUPIED:
        print("⚠️ Location Occupied")


enroller = Enroll(on_status=feedback)

# LED ها دست برنامه‌نویس است
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
identifier = Identify()
identifier.upload_to_sensor(data, 1)
if identifier.authenticate() == IdentifyStatus.SUCCESS:
    print(f"Authenticated ID: {identifier.loc_id}")
    identifier.config_led(LED["succes"])
else:
    identifier.config_led(LED["error"])
identifier.close()
