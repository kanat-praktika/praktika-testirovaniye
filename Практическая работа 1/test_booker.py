import requests

BASE_URL = "https://restful-booker.herokuapp.com"

def test_get_bookings():
    response = requests.get(f"{BASE_URL}/booking")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert isinstance(response.json(), list), "Ответ сервера должен быть списком"
    print("✓ TC-01 (GET /booking): PASSED")


def test_invalid_dates_bug():
    payload = {
        "firstname": "Batyr",
        "lastname": "Test",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-12-01",
            "checkout": "2026-01-01"
        },
        "additionalneeds": "Breakfast"
    }
    response = requests.post(f"{BASE_URL}/booking", json=payload)

    try:
        assert response.status_code == 400, f"Bug detected! Server allowed wrong dates with status {response.status_code}"
        print("✓ TC-03: PASSED")
    except AssertionError as e:
        print(f"❌ TC-03: FAILED. {e}")


if __name__ == "__main__":
    print("test loading..")
    test_get_bookings()
    test_invalid_dates_bug()
    print("test ended")