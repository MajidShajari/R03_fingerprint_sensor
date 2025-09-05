from src.config import ENCRYPTED_PATH
from src.features.encrypt import Encrypt
from src.features.enroll import Enroll


def main():
    try:
        finger = Enroll()
        encryptor = Encrypt()
        print("Fingerprint sensor initialized successfully.")
        # Add additional operations with the sensor here
    except Exception as e:
        print(f"Error initializing fingerprint sensor: {e}")
    finger_raw = finger.get_raw()
    encryptor.encrypt_to_file(ENCRYPTED_PATH + "/test.bin", bytes(finger_raw), "11235813")


if __name__ == "__main__":
    main()
