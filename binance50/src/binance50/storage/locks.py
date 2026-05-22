import os
import time
from pathlib import Path
from binance50.config.models import AppConfig
from binance50.core.exceptions import StorageLockError
from binance50.storage.paths import get_lock_dir, sanitize_path_component

class StorageLock:
    def __init__(self, config: AppConfig):
        self.config = config
        self.lock_dir = get_lock_dir(config)

    def _get_lock_path(self, lock_name: str) -> Path:
        safe_name = sanitize_path_component(lock_name)
        return self.lock_dir / f"{safe_name}.lock"

    def acquire(self, lock_name: str, timeout_seconds: float = 10) -> None:
        lock_path = self._get_lock_path(lock_name)
        start_time = time.time()

        while time.time() - start_time < timeout_seconds:
            try:
                # Exclusive creation
                fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                return
            except FileExistsError:
                # Check for stale lock
                try:
                    with open(lock_path, 'r') as f:
                        pid_str = f.read().strip()
                        if pid_str:
                            pid = int(pid_str)
                            # Extremely simple "is process running" check (Unix mostly)
                            try:
                                os.kill(pid, 0)
                            except OSError:
                                # Process is dead, stale lock
                                try:
                                    os.unlink(lock_path)
                                except FileNotFoundError:
                                    pass
                                continue # Try to acquire again
                except Exception:
                    pass
                time.sleep(0.1)

        raise StorageLockError(f"Could not acquire lock {lock_name} within {timeout_seconds}s")

    def release(self, lock_name: str) -> None:
        lock_path = self._get_lock_path(lock_name)
        try:
            os.unlink(lock_path)
        except FileNotFoundError:
            pass

    def is_locked(self, lock_name: str) -> bool:
        lock_path = self._get_lock_path(lock_name)
        return lock_path.exists()
