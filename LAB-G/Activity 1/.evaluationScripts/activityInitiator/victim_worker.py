#!/usr/bin/env python3
import os
import time

import requests

BASE_URL = os.environ.get("LABG_BASE_URL", "http://127.0.0.1:30000")
VICTIM_KEY = os.environ.get("VICTIM_KEY", "labg-default-victim-key")
SLEEP_SECONDS = int(os.environ.get("LABG_VICTIM_INTERVAL", "12"))


def tick() -> None:
    headers = {"X-Lab-Victim-Key": VICTIM_KEY}
    try:
        requests.post(f"{BASE_URL}/api/victim/visit", headers=headers, timeout=3)
    except Exception:
        # Keep worker resilient. App might still be starting.
        pass


if __name__ == "__main__":
    while True:
        tick()
        time.sleep(SLEEP_SECONDS)
