from src.core.sensor import FingerprintSensor


def main():
    try:
        _ = FingerprintSensor()
        print("Fingerprint sensor initialized successfully.")
        # Add additional operations with the sensor here
    except Exception as e:
        print(f"Error initializing fingerprint sensor: {e}")


if __name__ == "__main__":
    main()
