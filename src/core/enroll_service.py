# Standard Library
import time
from typing import Callable, Dict, Optional

# Third Library
import adafruit_fingerprint

from src.config import settings
from src.core.sensor_service import FingerprintSensorError, FingerprintSensorService
from src.core.status import SensorStatus
from src.utils.logger import setup_logger


class FingerEnrollService(FingerprintSensorService):
    """
    Handles enrollment (registration) and image capture of fingerprints.
    Inherits base sensor communication from FingerprintSensor.
    """

    def __init__(
        self,
        port: Optional[str] = None,
        baudrate: Optional[int] = None,
        on_status: Optional[Callable] = None,
    ):
        super().__init__(port, baudrate, on_status)
        self.logger = setup_logger("FingerEnrollService")

    # -----------------------------
    #   ENROLLING NEW FINGERPRINT
    # -----------------------------

    def enroll_finger(self) -> Dict:
        """
        Enroll fingerprint.

        Returns a dict with status and message.
        """
        try:
            self.logger.info("🟢 Starting fingerprint enrollment")

            # Step 1 - Ask to place finger
            self.send(SensorStatus.PLACE_FINGER, message="Place your finger on the sensor")

            if not self.capture(settings.CAPTURE_TIME_OUT, buffer=1):
                return self.send(SensorStatus.FAIL, "Failed to read first image")
            # Step 2: Remove finger
            self.send(SensorStatus.REMOVE_FINGER, message="Remove your finger")
            time.sleep(2)

            # Step 3: Place same finger again
            self.send(SensorStatus.PLACE_SAME_FINGER, message="Place the same finger again")

            if not self.capture(settings.CAPTURE_TIME_OUT, buffer=2):
                return self.send(SensorStatus.FAIL, message="Failed to read second image")

            # Step 4: Combine model
            self.send(SensorStatus.PROCESSING, message="Combining fingerprint images...")
            status = self._sensor.create_model()
            # Step 5: Handle results
            if status == adafruit_fingerprint.OK:
                raw_data = self._sensor.get_fpdata("image", slot=1)
                return self.send(SensorStatus.SUCCESS, message="Enrollment successful", data=raw_data)
            if status == adafruit_fingerprint.ENROLLMISMATCH:
                return self.send(SensorStatus.ENROLLMISMATCH, message="Fingerprints not matched")
            return self.send(SensorStatus.FAIL, message=f"Model creation failed (code: {status})")

        except FingerprintSensorError as e:
            return self.send(SensorStatus.FAIL, message=f"Sensor error: {e}")

        except Exception as e:
            return self.send(SensorStatus.FAIL, message=f"Unexpected error: {e}")
