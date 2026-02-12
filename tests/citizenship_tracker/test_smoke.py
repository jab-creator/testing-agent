import os
import time
import pytest
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

try:
    # Optional fallback if chromedriver isn't on PATH
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_WDM = True
except Exception:
    HAS_WDM = False


@pytest.fixture(scope="session")
def base_url():
    base_url_env = os.getenv("QA_BASE_URL_ENV", "APP_BASE_URL")
    return os.getenv(base_url_env, os.getenv("APP_BASE_URL", "http://localhost:8000/"))


@pytest.fixture(scope="session")
def smoke_paths():
    raw = os.getenv("QA_SMOKE_ENDPOINTS", "")
    if not raw.strip():
        return ["/"]
    paths = [p.strip() for p in raw.split(",") if p.strip()]
    return paths or ["/"]


@pytest.fixture
def driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    # Prefer system chromedriver if installed (best on WSL)
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


def wait_for_any_text(driver, texts, timeout=12):
    end = time.time() + timeout
    texts_l = [t.lower() for t in texts]
    while time.time() < end:
        src = driver.page_source.lower()
        if any(t in src for t in texts_l):
            return True
        time.sleep(0.25)
    return False


def test_app_loads(driver, base_url, smoke_paths):
    for path in smoke_paths:
        driver.get(urljoin(base_url, path))
        # Generic "did we load anything real?"
        assert wait_for_any_text(driver, ["citizen", "citizenship", "days in canada", "progress"], timeout=12)


def test_core_nav_visible(driver, base_url):
    driver.get(urljoin(base_url, "/"))

    # These are intentionally loose (text-based) for first pass
    assert wait_for_any_text(driver, ["dashboard", "trips", "settings"], timeout=12)
