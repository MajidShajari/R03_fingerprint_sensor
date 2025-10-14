import time
from typing import Callable, Dict, Optional

import adafruit_fingerprint
import serial
from serial import SerialException

from src.config import settings
from src.core.status import SensorStatus
from src.utils.logger import setup_logger


class FingerprintSensorError(Exception):
    """Base exception for fingerprint sensor errors."""


class FingerprintSensorService:
    def __init__(
        self,
        port: Optional[str] = None,
        baudrate: Optional[str] = None,
        on_status: Optional[Callable[[SensorStatus], None]] = None,
    ):
        """
        Initialize fingerprint sensor over UART.
        Raises FingerprintSensorError if connection fails.
        """
        self.logger = setup_logger("FingerprintSensor")
        self._port = port or settings.PORT
        self._baudrate = baudrate or settings.BAUDRATE
        self._timeout = settings.SENSOR_TIME_OUT
        self.on_status = on_status or (lambda status, msg=None: None)

        try:
            uart = serial.Serial(self._port, baudrate=self._baudrate, timeout=self._timeout)
            if not uart.is_open:
                raise FingerprintSensorError("UART port not open")
            self._sensor = adafruit_fingerprint.Adafruit_Fingerprint(uart)
            self.logger.info("Fingerprint sensor initialized successfully.")
        except SerialException as e:
            self.logger.exception("SerialException: Could not connect to sensor.")
            raise FingerprintSensorError("Sensor not connected") from e
        except Exception as e:
            self.logger.exception("Unexpected error initializing sensor.")
            raise FingerprintSensorError("Unknown sensor error") from e

    def send(self, status: SensorStatus, msg: str = ""):
        self.logger.info(f"[{status.name}] {msg}")
        if self.on_status:
            self.on_status(status, msg)

    def response(self, status=SensorStatus.FAIL, **kwargs) -> dict:
        """
        Build a standardized response dictionary for sensor or service operations.
        Example:
            return make_response(SensorStatus.SUCCESS, message="Done", data=[1, 2, 3])
            # =>
            {"status": SensorStatus.SUCCESS, "message": "Done", "data": [1, 2, 3]}
        Args:
            status (SensorStatus): Enum representing the current operation result.
            **kwargs: Any additional fields (e.g., message, data, id, meta).
        Returns:
            dict: A consistent response object.
        """
        response = {"status": status}

        # Default message based on status name (if not provided)
        response["message"] = kwargs.pop("message", status.name if hasattr(status, "name") else str(status))

        # Merge additional keyword arguments (e.g., data, meta, id)
        response.update(kwargs)

        return response

    # -------------------------
    #   Sensor Core Methods
    # -------------------------
    def capture(self, timeout: int = 5, buffer: int = 1) -> bool:
        self.logger.info("capture finger image... ")
        start_time = time.time()
        while (time.time() - start_time) <= timeout:
            status = self._sensor.get_image()
            if status == adafruit_fingerprint.OK:
                self.logger.info("Fingerprint image captured successfully.")
                if self._template(buffer):
                    return True
            if status == adafruit_fingerprint.NOFINGER:
                self.send(SensorStatus.PLACE_FINGER, "Place your finger on the sensor")
                time.sleep(0.8)
                continue
            if status == adafruit_fingerprint.IMAGEFAIL:
                self.logger.error("Imaging error.")
                break
            self.logger.error("Unknown error while capturing image.")
            break
        self.logger.error("Timeout or failed to read finger.")
        return False

    def _template(self, buffer: int = 1):
        self.logger.info("Templating...")
        status = self._sensor.image_2_tz(buffer)
        if status == adafruit_fingerprint.OK:
            self.logger.info("Templated")
            return True
        if status == adafruit_fingerprint.IMAGEMESS:
            self.logger.error("Image too messy")
        elif status == adafruit_fingerprint.FEATUREFAIL:
            self.logger.error("Could not identify features")
        elif status == adafruit_fingerprint.INVALIDIMAGE:
            self.logger.error("Image invalid")
        else:
            self.logger.error("Other error")
        return False

    # -------------------------
    #   Sensor Info
    # -------------------------
    def get_sensor_info(self):
        return {
            "templates_list": self._sensor.templates,
            "templates_count": len(self._sensor.templates or []),
            "library_size": getattr(self._sensor, "library_size", None),
        }

    # -------------------------
    #   LED Control
    # -------------------------

    def config_led(self, mode: Dict) -> None:
        """Configure the sensor LED according to given mode dict."""
        try:
            self._sensor.set_led(
                color=mode.get("color", 0),
                mode=mode.get("mode", 2),
                cycles=mode.get("cycle", 20),
                speed=mode.get("speed", 128),
            )
            self.logger.debug("LED configured: %s", mode)
            time.sleep(0.2)
        except Exception as e:
            self.logger.warning("⚠️ Failed to configure LED: %s", e)

    # -------------------------
    #   Cleanup
    # -------------------------
    def clear_library(self):
        try:
            if self._sensor.empty_library() == adafruit_fingerprint.OK:
                self.logger.info("🔴 Sensor connection closed.")
                return True
            return False
        except Exception as e:
            self.logger.warning("Failed to empty library in sensor: %s", e)
            return False

    def close(self):
        """Safely turn off LED and close UART connection."""
        try:
            self._sensor.set_led(mode=4)  # LED off
            self.__del__()
            self.logger.info("🔴 Sensor connection closed.")
        except Exception:
            pass

    def __del__(self):
        """Destructor to ensure safe resource cleanup."""
        try:
            self._sensor.close_uart()
        except Exception as e:
            self.logger.warning("Failed to close sensor: %s", e)
