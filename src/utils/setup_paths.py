from src.config import ALL_PATHS


def ensure_paths():
    for path in ALL_PATHS:
        path.mkdir(parents=True, exist_ok=True)
