import time
from typing import Dict

import adafruit_fingerprint
import serial
from serial import SerialException

from src.config import BAUDRATE, PORT, SENSOR_TIME_OUT
from src.utils.logger import setup_logger

from .exceptions import FingerprintSensorError

local_logger = setup_logger("Sensor")


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
        except SerialException as e:
            local_logger.exception("SerialException: Could not connect to sensor.")
            raise FingerprintSensorError("Sensor not connected") from e
        except Exception as e:
            local_logger.exception("Unexpected error initializing sensor.")
            raise FingerprintSensorError("Unknown sensor error") from e

    def _capture(self, timeout: int = 5, buffer: int = 1) -> bool:
        local_logger.info("capture finger image... ")
        start_time = time.time()
        while (time.time() - start_time) <= timeout:
            status = self._sensor.get_image()
            local_logger.info("Fingerprint image captured.")
            if status == adafruit_fingerprint.OK:
                if self._template(buffer):
                    return True
            if status == adafruit_fingerprint.NOFINGER:
                time.sleep(1)
                continue
            if status == adafruit_fingerprint.IMAGEFAIL:
                local_logger.error("Imaging error.")
                break
            local_logger.error("Unknown error while capturing image.")
            break
        local_logger.error("Timeout or failed to read finger.")
        return False

    def _template(self, buffer: int = 1):
        local_logger.info("Templating...")
        status = self._sensor.image_2_tz(buffer)
        if status == adafruit_fingerprint.OK:
            local_logger.info("Templated")
            return True
        if status == adafruit_fingerprint.IMAGEMESS:
            local_logger.error("Image too messy")
        elif status == adafruit_fingerprint.FEATUREFAIL:
            local_logger.error("Could not identify features")
        elif status == adafruit_fingerprint.INVALIDIMAGE:
            local_logger.error("Image invalid")
        else:
            local_logger.error("Other error")
        return False

    def config_led(self, mode: Dict) -> None:
        """Configure sensor LED according to given mode dict."""
        try:
            self._sensor.set_led(
                color=mode.get("color", 0),
                mode=mode.get("mode", 2),
                cycles=mode.get("cycle", 20),
                speed=mode.get("speed", 128),
            )
            time.sleep(0.2)
        except Exception as e:
            local_logger.warning("Failed to configure LED :%s", e)

    def close(self):
        try:
            self._sensor.set_led(mode=4)
            self._sensor.close_uart()
        except Exception as e:
            local_logger.warning("Failed to close sensor: %s", e)
