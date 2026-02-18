from __future__ import annotations

import pytest

from tests.citizenship_tracker.helpers import fetch


@pytest.mark.regression
def test_app_startup_healthcheck_endpoint(http_session, base_url):
    response = fetch(http_session, base_url, "/")
    assert response.status_code == 200


@pytest.mark.regression
@pytest.mark.parametrize(
    ("path", "expected_text"),
    [
        ("/index.html", "Days in Canada"),
        ("/share.html", "Loading citizenship progress"),
        ("/demo-share.html", "Progress Overview"),
    ],
)
def test_critical_pages_return_success(http_session, base_url, path, expected_text):
    response = fetch(http_session, base_url, path)
    assert response.status_code == 200
    assert expected_text in response.text


@pytest.mark.regression
@pytest.mark.parametrize(
    ("path", "expected_text"),
    [
        ("/styles.css", ".stats-grid"),
        ("/script.js", "Days in Canada"),
    ],
)
def test_critical_assets_return_success(http_session, base_url, path, expected_text):
    response = fetch(http_session, base_url, path)
    assert response.status_code == 200
    assert expected_text in response.text


@pytest.mark.regression
def test_settings_workflow_fields_are_rendered(http_session, base_url):
    response = fetch(http_session, base_url, "/")
    assert response.status_code == 200
    assert 'id="prDate"' in response.text
    assert 'id="targetDate"' in response.text
    assert 'id="residencyStatus"' in response.text
    assert 'id="saveSettingsBtn"' in response.text

