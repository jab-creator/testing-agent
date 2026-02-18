from __future__ import annotations

import os

import pytest
import requests


@pytest.fixture(scope="session")
def base_url() -> str:
    base_url_env = os.getenv("QA_BASE_URL_ENV", "APP_BASE_URL")
    return os.getenv(base_url_env, os.getenv("APP_BASE_URL", "http://localhost:8000/"))


@pytest.fixture(scope="session")
def http_session() -> requests.Session:
    session = requests.Session()
    yield session
    session.close()
