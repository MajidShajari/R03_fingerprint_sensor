import asyncio
import sys
from pathlib import Path

from src.core.fingerprint_service import (
    FingerprintError,
    authenticate_with_encrypted,
    check_sensor,
    enroll_fingerprint,
    reset_sensor,
)
from src.utils.logger import setup_logger

logger = setup_logger("FingerprintCLI")


# -------------------------------------------------------------------
# Helper for async-safe CLI input
# -------------------------------------------------------------------
async def ainput(prompt: str) -> str:
    """Async version of input() to allow usage with asyncio.run."""
    return await asyncio.to_thread(input, prompt)


# -------------------------------------------------------------------
# CLI Operations
# -------------------------------------------------------------------
async def cli_check_sensor():
    print("\n🔍 Checking fingerprint sensor connection...")
    result = await check_sensor()
    print("✅ Sensor status:", result)


async def cli_enroll():
    user_id = await ainput("Enter user ID for enrollment: ")
    print(f"\n🌀 Starting enrollment for user: {user_id}")
    try:
        result = await enroll_fingerprint(user_id)
        print(f"✅ Enrollment complete. Encrypted file: {result['encrypted_path']}")
    except FingerprintError as e:
        print(f"❌ Enrollment failed: {e.message}")


async def cli_authenticate():
    choice = await ainput("Authenticate using (1) user_id or (2) file path? [1/2]: ")
    if choice.strip() == "1":
        user_id = await ainput("Enter user ID: ")
        try:
            result = await authenticate_with_encrypted(user_id=user_id)
            if result.get("status") == "not found":
                print("❌ not found fingerprint")
            if result.get("status") == "ok":
                print("✅ found fingerprint")
        except FingerprintError as e:
            print(f"❌ Authentication failed: {e.message}")
    else:
        file_path = await ainput("Enter encrypted file path: ")
        if not Path(file_path).exists():
            print("❌ File not found.")
            return
        try:
            result = await authenticate_with_encrypted(file_path=file_path)
            if result.get("status") == "not found":
                print("❌ not found fingerprint")
            if result.get("status") == "ok":
                print("✅ found fingerprint")
        except FingerprintError as e:
            print(f"❌ Authentication failed: {e.message}")


async def cli_reset_sensor():
    print("\n⚠️ Resetting fingerprint sensor memory...")
    try:
        result = await reset_sensor()
        print("✅ Reset complete:", result)
    except FingerprintError as e:
        print(f"❌ Reset failed: {e.message}")


# -------------------------------------------------------------------
# Main Menu Loop
# -------------------------------------------------------------------
async def main():
    MENU = """
==============================
 🔒 Fingerprint Manager CLI
==============================
[1] Check Sensor
[2] Enroll Fingerprint
[3] Authenticate Fingerprint
[4] Reset Sensor Memory
[0] Exit
------------------------------
"""

    while True:
        print(MENU)
        await asyncio.sleep(2.5)
        choice = await ainput("Select an option: ")
        if choice == "1":
            await cli_check_sensor()
        elif choice == "2":
            await cli_enroll()
        elif choice == "3":
            await cli_authenticate()
        elif choice == "4":
            await cli_reset_sensor()
        elif choice == "0":
            print("👋 Exiting...")
            sys.exit(0)
        else:
            print("❌ Invalid option, please try again.")
        await asyncio.sleep(2.5)
        print("\nPress Enter to continue...")
        await ainput("")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Exited by user.")
