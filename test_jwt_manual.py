import requests
import sys

BASE_URL = "http://127.0.0.1:8001"

def test_jwt():
    print("1. Testing access without token...")
    try:
        r = requests.get(f"{BASE_URL}/")
        if r.status_code == 401:
            print("   PASS: Got 401 as expected")
        else:
            print(f"   FAIL: Expected 401, got {r.status_code}")
            print(r.text)
    except Exception as e:
        print(f"   FAIL: Could not connect: {e}")
        return

    print("\n2. Testing login...")
    login_data = {
        "username": "johndoe",
        "password": "secret"
    }
    try:
        r = requests.post(f"{BASE_URL}/token", data=login_data)
        if r.status_code == 200:
            token = r.json().get("access_token")
            print("   PASS: Login successful, got token")
        else:
            print(f"   FAIL: Login failed: {r.status_code}")
            print(r.text)
            return
    except Exception as e:
        print(f"   FAIL: Login error: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    print("\n3. Testing access with token...")
    try:
        r = requests.get(f"{BASE_URL}/", headers=headers)
        if r.status_code == 200:
            print(f"   PASS: Got 200 OK. Response: {r.json()}")
        else:
            print(f"   FAIL: Expected 200, got {r.status_code}")
            print(r.text)
    except Exception as e:
        print(f"   FAIL: Error: {e}")

    print("\n4. Testing protected /test endpoint...")
    try:
        r = requests.get(f"{BASE_URL}/test", headers=headers)
        if r.status_code == 200:
            print(f"   PASS: Got 200 OK. Response: {r.json()}")
        else:
            print(f"   FAIL: Expected 200, got {r.status_code}")
            print(r.text)
    except Exception as e:
        print(f"   FAIL: Error: {e}")

if __name__ == "__main__":
    test_jwt()
