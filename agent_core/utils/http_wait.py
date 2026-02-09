from __future__ import annotations
import time
import requests

def wait_for_url(url: str, timeout_s: int = 20, interval_s: float = 0.5) -> None:
    end = time.time() + timeout_s
    last_err = None
    while time.time() < end:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code < 500:
                return
        except Exception as e:
            last_err = e
        time.sleep(interval_s)
    raise TimeoutError(f"Timed out waiting for {url}. Last error: {last_err}")
