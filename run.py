"""Launch backend and frontend together for local development."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent


def wait_for_backend(timeout=120):
    url = "http://127.0.0.1:8000/health"
    for _ in range(timeout):
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def main():
    env = os.environ.copy()

    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(ROOT),
        env=env,
    )

    try:
        if not wait_for_backend():
            raise RuntimeError("Backend did not start in time.")

        frontend = subprocess.Popen(
            [sys.executable, "frontend/frontend.py"],
            cwd=str(ROOT),
            env=env,
        )

        print("Backend:  http://127.0.0.1:8000/docs")
        print("Frontend: http://127.0.0.1:7860")
        print("Press Ctrl+C to stop.")

        while True:
            if backend.poll() is not None:
                break
            if frontend.poll() is not None:
                break
            time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        for proc in [backend]:
            if proc and proc.poll() is None:
                proc.terminate()


if __name__ == "__main__":
    main()
