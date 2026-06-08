import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"


def test_get_all_bookings_status_and_type():
    response = requests.get(f"{BASE_URL}/booking")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_booking_valid_data():
    payload = {
        "firstname": "Batyr",
        "lastname": "Test",
        "totalprice": 200,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-07-01",
            "checkout": "2026-07-10"
        },
        "additionalneeds": "Dinner"
    }
    response = requests.post(f"{BASE_URL}/booking", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "bookingid" in data
    assert data["booking"]["firstname"] == "Batyr"


def test_update_booking_unauthorized_forbidden():
    payload = {
        "firstname": "Batyr",
        "lastname": "Updated",
        "totalprice": 180,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-07-01",
            "checkout": "2026-07-10"
        },
        "additionalneeds": "None"
    }
    response = requests.put(f"{BASE_URL}/booking/1", json=payload)
    assert response.status_code == 403


def test_bug_date_inversion_validation():
    payload = {
        "firstname": "Batyr",
        "lastname": "Test",
        "totalprice": 100,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-12-01",
            "checkout": "2026-01-01"
        },
        "additionalneeds": "Breakfast"
    }
    response = requests.post(f"{BASE_URL}/booking", json=payload)
    assert response.status_code == 400

if __name__ == '__main__':
    test_update_booking_unauthorized_forbidden()
    test_get_all_bookings_status_and_type()
    test_create_booking_valid_data()
    test_bug_date_inversion_validation()