import requests

BASE_URL_1 = 'http://auth_service:5000'

BASE_URL_2 = 'http://localhost:5000'

BASE_URL_3 = 'http://127.0.0.1:5000'

print("start test connect")


def ping():
    correct_connection = 0
    data = []
    for BASE_URL in [BASE_URL_1, BASE_URL_2, BASE_URL_3]:
        try:
            response = requests.post(BASE_URL + '/auth/login', json={
                'name': 'homeuser',
                'password': 'changeme'
            })
            data.append(response.json())
            print("Connect successful")
            correct_connection += 1
        except Exception as e:
            print("Connect retry?")
            print(e)
    return data, correct_connection


print(ping())

print("end test connect")
