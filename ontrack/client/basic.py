from getpass import getpass

import requests

auth_endpoint = "http://localhost:8000/api/token/"
username = input("What is your username?\n")
password = getpass("What is your password?\n")

auth_response = requests.post(
    auth_endpoint, json={"username": username, "password": password}
)
print(auth_response.json())

if auth_response.status_code == 200:
    token = auth_response.json()["access"]
    headers = {"Authorization": f"Bearer {token}"}
    endpoint = "http://localhost:8000/api/market/task/eod/equity/"

    data = {"exchange": "nse"}
    response = requests.put(endpoint, headers=headers, data=data)

    data = response.json()
    print(data)
