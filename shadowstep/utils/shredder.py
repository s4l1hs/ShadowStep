import os
import random
from .logger import log

def secure_delete(file_path, passes=3):
    """
    Securely deletes the specified file by overwriting it with random data.
    Simulates the DoD 5220.22-M standard.
    """
    if not os.path.exists(file_path):
        log.error(f"File not found: {file_path}")
        return False

    try:
        file_size = os.path.getsize(file_path)
        log.info(f"Secure delete started: {file_path} ({passes} passes)")

        with open(file_path, "ba+") as f:
            for i in range(passes):
                f.seek(0)
                # Random bytes (os.urandom is sufficient for speed here)
                random_data = os.urandom(file_size)
                f.write(random_data)
                f.flush()
                os.fsync(f.fileno())
                log.debug(f" -> Pass {i+1}/{passes} completed.")

        os.remove(file_path)
        log.info(f"File successfully destroyed: {file_path}")
        return True

    except PermissionError:
        log.error(f"Access denied: {file_path}")
        return False
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        return False