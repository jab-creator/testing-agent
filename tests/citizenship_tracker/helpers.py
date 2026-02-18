from __future__ import annotations

from urllib.parse import urljoin

import requests


def fetch(http_session: requests.Session, base_url: str, path: str) -> requests.Response:
    return http_session.get(urljoin(base_url, path), timeout=5)

