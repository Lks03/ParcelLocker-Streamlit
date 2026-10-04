"""JSON persistence, shared by the CLI and Streamlit views."""
import json
import os
import tempfile
from pathlib import Path


class StorageError(RuntimeError):
    pass


class ParcelRepository:
    def __init__(self, path):
        self.path = Path(path)

    def load(self):
        if not self.path.exists():
            return None
        try:
            with self.path.open(encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict) or not all(isinstance(data.get(k), list) for k in ("lockers", "parcels")):
                raise ValueError("Invalid data format")
            return data
        except (OSError, ValueError) as error:
            raise StorageError("Cannot read data.json. Check the file or restore a backup; existing data has not been replaced.") from error

    def save(self, data):
        temporary = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.path.parent, suffix=".tmp", delete=False) as file:
                temporary = file.name
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, self.path)
        except OSError as error:
            raise StorageError("Could not save the operation. Check folder permissions and available disk space, then try again.") from error
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)
