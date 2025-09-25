# R503 Fingerprint Sensor

A Python project for enrolling, encrypting, storing, and identifying fingerprints using the R503 fingerprint sensor. The project provides a modular structure for sensor interaction, data encryption, and status feedback.

## Features

- Enroll fingerprints and store them securely.
- Encrypt and decrypt fingerprint data using AES-GCM.
- Identify fingerprints by uploading and matching data.
- Modular codebase with clear separation of concerns.
- Logging and error handling for robust operation.

## Project Structure

```text
R503_fingerprint_sensor/
├── main.py                      # Main script for enrolling and identifying fingerprints
├── pyproject.toml               # Project metadata and dependencies
├── src/
|	├── config.py                # Configuration (paths, sensor settings, LED, timeouts)
|	├── core/
|	|	├── enroll.py            # Enrollment logic
|	|	├── identify.py          # Identification logic
|	|	├── sensor.py            # Sensor communication and base class
|	|	├── status.py            # Status enums for feedback
|	|	└── exceptions.py        # Custom exceptions
|	├── security/
|	|	└── encrypt.py           # Encryption and decryption logic
|	└── utils/
|		├── logger.py            # Logger setup
|		└──setup_paths.py        # Ensures required directories exist
├── data/
|	├── encrypted/               # Stores encrypted fingerprint data
|	├── decrypted/               # Stores decrypted fingerprint data
|	├── logs/                    # Log files
|	└── tmp/                     # Temporary files
```

## Quick Start

1. **Install dependencies**  
	 Ensure Python 3.12+ is installed.  
	 Install dependencies:
        use the dependencies listed in `pyproject.toml`.

2. **Connect the R503 sensor**  
	 Update the `PORT` in `src/config.py` if needed.

3. **Run the main script**  
	 ```
	 python main.py
	 ```

## How It Works

- The script enrolls a fingerprint, encrypts the data, saves it, decrypts it, and uploads it back to the sensor for identification.
- Status feedback is provided in the console and via LED configuration.
- All sensitive data is encrypted before storage.

## Dependencies

- `adafruit-circuitpython-fingerprint`
- `cryptography`
- `rich`

## Logging

Logs are stored in `data/logs/` with daily rotation.

---

Let me know if you want to add usage examples, API documentation, or more details!
