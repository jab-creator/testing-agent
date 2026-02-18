from __future__ import annotations

import pytest

from tests.citizenship_tracker.helpers import (
    load_eligibility_fixture,
    run_independent_expected_calc,
    seed_app_data,
)


FIXTURE_FILES = [
    "test-data.json",
    "test-data-simple-mode.json",
    "test-data-complex-absences.json",
    "test-data-pr-only.json",
    "test-data-overlap-trips.json",
]


@pytest.mark.regression
@pytest.mark.parametrize("fixture_name", FIXTURE_FILES)
def test_eligibility_calculation_matches_expected_formula(driver, base_url, fixture_name):
    fixture_data = load_eligibility_fixture(fixture_name)
    seed_app_data(driver, base_url, fixture_data)

    actual = driver.execute_script("return window.citizenshipTracker.calculateDaysInCanada();")
    expected = run_independent_expected_calc(driver, fixture_data)

    assert int(actual["daysInCanada"]) == int(expected["daysInCanada"])
    assert int(actual.get("daysOutside", 0)) == int(expected["daysOutside"])
    assert int(actual.get("totalDaysInPeriod", 0)) == int(expected["totalDaysInPeriod"])

    dashboard_days = driver.find_element("id", "daysInCanada").text.replace(",", "").strip()
    assert int(dashboard_days) == int(actual["daysInCanada"])


@pytest.mark.regression
@pytest.mark.parametrize("fixture_name", ["test-data.json", "test-data-complex-absences.json"])
def test_empty_pr_date_is_not_eligible(driver, base_url, fixture_name):
    fixture_data = load_eligibility_fixture(fixture_name)
    seed_app_data(driver, base_url, fixture_data)

    calc = driver.execute_script("return window.citizenshipTracker.calculateDaysInCanada();")
    remaining = driver.find_element("id", "daysRemaining").text.replace(",", "").strip()

    assert int(calc["daysInCanada"]) == 0
    assert int(remaining) == 1095

