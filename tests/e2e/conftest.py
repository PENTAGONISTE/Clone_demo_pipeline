import os
import socket
import subprocess
import sys
import time

import pytest


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def base_url(tmp_path_factory):
    """Démarre Biblio sur une base SQLite jetable, sauf si --base-url est fourni."""
    if url := os.getenv("E2E_BASE_URL"):
        yield url
        return
    port = _free_port()
    env = {**os.environ, "DATABASE_URL": f"sqlite:///{tmp_path_factory.mktemp('e2e')}/e2e.db"}
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(port)],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}"
    for _ in range(50):
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
            break
        except OSError:
            time.sleep(0.2)
    yield url
    proc.terminate()
    proc.wait()
