import time
from typing import Dict

import adafruit_fingerprint
import serial

from src.config import BAUDRATE, LED, PORT, SENSOR_TIME_OUT
from src.logger import setup_logger

from .exceptions import FingerprintSensorError

local_logger = setup_logger()


class FingerprintSensor:
    def __init__(self):
        """
        Initialize fingerprint sensor over UART.
        Raises FingerprintSensorError if connection fails.
        """
        try:
            uart = serial.Serial(PORT, baudrate=BAUDRATE, timeout=SENSOR_TIME_OUT)
            if not uart.is_open:
                raise FingerprintSensorError("UART port not open")
            self._sensor = adafruit_fingerprint.Adafruit_Fingerprint(uart)
            local_logger.info("Fingerprint sensor initialized successfully.")
            self.config_led(LED.get("on", {"color": 7, "mode": 1, "cycle": 20, "speed": 250}))
        except Exception as e:
            local_logger.exception("Unexpected error initializing sensor.")
            raise FingerprintSensorError("Unknown sensor error") from e

    def config_led(self, mode: Dict) -> None:
        """Configure sensor LED according to given mode dict."""
        try:
            self._sensor.set_led(
                color=mode.get("color", 0),
                mode=mode.get("mode", 2),
                cycles=mode.get("cycle", 20),
                speed=mode.get("speed", 128),
            )
            time.sleep(0.5)
        except Exception as e:
            local_logger.warning("Failed to configure LED :%s", e)

    def close(self):
        self.config_led(LED.get("off", {"mode": 4}))
        self._sensor.soft_reset()
