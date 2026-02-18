from __future__ import annotations

import os

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

try:
    from webdriver_manager.chrome import ChromeDriverManager

    HAS_WDM = True
except Exception:
    HAS_WDM = False


@pytest.fixture(scope="session")
def base_url() -> str:
    base_url_env = os.getenv("QA_BASE_URL_ENV", "APP_BASE_URL")
    return os.getenv(base_url_env, os.getenv("APP_BASE_URL", "http://localhost:8000/"))


@pytest.fixture(scope="session")
def http_session() -> requests.Session:
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture
def driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    service = None
    for path in ("/usr/bin/chromedriver", "/snap/bin/chromedriver"):
        if os.path.exists(path):
            service = Service(path)
            break

    if service is None and HAS_WDM:
        service = Service(ChromeDriverManager().install())

    if service is None:
        raise RuntimeError("No chromedriver found. Install chromium-chromedriver or chromium-driver.")

    d = webdriver.Chrome(service=service, options=opts)
    d.set_window_size(1400, 900)
    yield d
    d.quit()
