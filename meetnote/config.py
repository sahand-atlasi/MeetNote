from pathlib import Path


def default_database_path() -> Path:
    return Path("data") / "meetnote.sqlite3"
