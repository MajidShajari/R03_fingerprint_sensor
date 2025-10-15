# Standard Library
from pathlib import Path

# Third Library
# THIRDPARTY
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "R503 Fingerprint Manager"
    # Base paths
    MAIN_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = MAIN_DIR / "data"

    # Paths
    CAPTURE_TMP_PATH: Path = DATA_DIR / "tmp"
    LOGGER_PATH: Path = DATA_DIR / "logs"
    ENCRYPTED_PATH: Path = DATA_DIR / "encrypted"

    # Serial
    PORT: str = "COM7"
    BAUDRATE: int = 57600

    # Timeouts
    SENSOR_TIME_OUT: int = 5
    CAPTURE_TIME_OUT: int = 20

    # LED Modes
    LED: dict = {
        "start": {"color": 7, "mode": 1, "cycle": 0, "speed": 250},
        "fail": {"color": 1, "mode": 2, "cycle": 20, "speed": 128},
        "p_finger": {"color": 2, "mode": 3, "cycle": 0, "speed": 128},
        "r_finger": {"color": 6, "mode": 2, "cycle": 0, "speed": 128},
        "process": {"color": 3, "mode": 1, "cycle": 0, "speed": 128},
        "off": {"color": 5, "mode": 4, "cycle": 0, "speed": 128},
        "success": {"color": 4, "mode": 3, "cycle": 20, "speed": 128},
    }
    # Secret Info
    SECRET_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def ensure_paths(self):
        """Create all necessary directories"""
        paths = [self.CAPTURE_TMP_PATH, self.LOGGER_PATH, self.ENCRYPTED_PATH]
        for path in paths:
            path.mkdir(parents=True, exist_ok=True)


# Instance
settings = Settings()
settings.ensure_paths()
