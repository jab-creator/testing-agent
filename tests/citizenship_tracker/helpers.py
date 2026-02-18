from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urljoin

import requests


def fetch(http_session: requests.Session, base_url: str, path: str) -> requests.Response:
    return http_session.get(urljoin(base_url, path), timeout=5)


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "eligibility"


def load_eligibility_fixture(filename: str) -> dict:
    return json.loads((FIXTURE_ROOT / filename).read_text(encoding="utf-8"))


def seed_app_data(driver, base_url: str, fixture_data: dict) -> None:
    trips = json.dumps(fixture_data.get("trips", []))
    settings = json.dumps(fixture_data.get("settings", {}))
    driver.get(base_url)
    driver.execute_script(
        """
        localStorage.setItem('citizenship-trips', arguments[0]);
        localStorage.setItem('citizenship-settings', arguments[1]);
        """,
        trips,
        settings,
    )
    driver.refresh()


def run_independent_expected_calc(driver, fixture_data: dict) -> dict:
    return driver.execute_script(
        """
        const data = arguments[0] || {};
        const settings = data.settings || {};
        const trips = data.trips || [];

        if (!settings.prDate) {
            return { daysInCanada: 0, daysOutside: 0, totalDaysInPeriod: 0 };
        }

        const today = new Date();
        const prDate = new Date(settings.prDate);
        const eligibilityPeriodEnd = today;
        const eligibilityPeriodStart = new Date(today);
        eligibilityPeriodStart.setFullYear(today.getFullYear() - 5);
        const actualStart = prDate > eligibilityPeriodStart ? prDate : eligibilityPeriodStart;

        const totalDaysInPeriod = Math.ceil((eligibilityPeriodEnd - actualStart) / (1000 * 60 * 60 * 24));

        let daysOutside = 0;
        trips.forEach((trip) => {
            const tripStart = new Date(trip.departureDate);
            const tripEnd = new Date(trip.returnDate);
            if (tripEnd >= actualStart && tripStart <= eligibilityPeriodEnd) {
                const overlapStart = tripStart > actualStart ? tripStart : actualStart;
                const overlapEnd = tripEnd < eligibilityPeriodEnd ? tripEnd : eligibilityPeriodEnd;
                if (overlapStart < overlapEnd) {
                    const totalDays = Math.ceil((overlapEnd - overlapStart) / (1000 * 60 * 60 * 24));
                    daysOutside += Math.max(0, totalDays - 1);
                }
            }
        });

        const daysInCanada = Math.max(0, totalDaysInPeriod - daysOutside - 1);
        return { daysInCanada, daysOutside, totalDaysInPeriod };
        """,
        fixture_data,
    )
