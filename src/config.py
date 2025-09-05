from pathlib import Path

# Sensor
PORT = "COM7"
BAUDRATE = 57600
# Ring led sensor
LED = {
    "on": {"color": 7, "mode": 1, "cycle": 20, "speed": 250},
    "ready": {"color": 7, "mode": 1, "cycle": 0, "speed": 250},
    "error": {"color": 1, "mode": 2, "cycle": 20, "speed": 128},
    "p_finger": {"color": 2, "mode": 3, "cycle": 0, "speed": 128},
    "r_finger": {"color": 6, "mode": 2, "cycle": 0, "speed": 128},
    "process": {"color": 3, "mode": 1, "cycle": 0, "speed": 128},
    "off": {"color": 5, "mode": 4, "cycle": 0, "speed": 128},
    "succes": {"color": 4, "mode": 3, "cycle": 20, "speed": 128},
}
# Timeouts
SENSOR_TIME_OUT = 5
CAPTURE_TIME_OUT = 20
# Path
CAPTURE_TMP_PATH = "data/tmp"
LOGGER_PATH = "data/logs"
ENCRYPTED_PATH = "data/encrypted"
DECRYPTED_PATH = "data/decrypted"
main_dir = Path(__file__).parent.parent
for path in [CAPTURE_TMP_PATH, LOGGER_PATH, ENCRYPTED_PATH, DECRYPTED_PATH]:
    full_path = main_dir / path
    if not full_path.exists():
        full_path.mkdir(parents=True, exist_ok=True)
