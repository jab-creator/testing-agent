from __future__ import annotations

import pytest

from tests.citizenship_tracker.helpers import fetch


@pytest.mark.smoke
def test_homepage_is_available(http_session, base_url):
    response = fetch(http_session, base_url, "/")
    assert response.status_code == 200
    assert "Canadian Citizenship Tracker" in response.text
