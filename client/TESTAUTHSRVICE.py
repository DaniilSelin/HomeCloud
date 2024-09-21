import requests
import os


"""Response: {'data': [{'created_at': '2024-08-11T10:28:09.427145', 
'expiry_date': '2024-09-10T10:28:09.415510', 'max_users': 1, 
'token': '73a49798-c391-4d40-ab5b-79592a086d85'}, 
{'created_at': '2024-08-11T10:29:57.183848',
 'expiry_date': '2024-09-10T10:29:57.183310', 'max_users': 1, 
 'token': '1ac9dfd8-718a-4b59-a552-65e6036b4936'}, {'created_at': '2024-08-11T10:32:06.860769', 'expiry_date': '2024-09-10T10:32:06.860197', 'max_users': 1, 'token': 'f2bff8c1-7e50-471a-85d8-123996b7a861'}, {'created_at': '2024-08-11T10:32:30.856932', 'expiry_date': '2024-09-10T10:32:30.856363', 'max_users': 1, 'token': 'c8a64ee9-bfba-4c5d-97ad-41f246e1a4c5'}, {'created_at': '2024-08-11T10:20:46.666386', 'expiry_date': '2024-09-10T10:20:46.663347', 'max_users': 10, 'token': '78126743-b1ee-4f6c-85ba-637396ad3869'}], 'message': 'Tokens retrieved successfully'}
"""
BASE_URL = 'http://127.0.0.1:5000'
response = requests.post(BASE_URL + '/auth/login', json={
        'name': 'homeuser',
        'password': 'changeme'
    })
data = response.json()
print(data)
access = data['data']['access_token']


import jwt


decoded = jwt.decode(access, '15517b618c60112042ea471f7609c160b4e59fda71d2099b', algorithms=["HS256"])
print(decoded)


def generate_token():
    response = requests.post(f'{BASE_URL}/auth/generate_token', headers={
        'Authorization': f'Bearer {access}'
    }, json={'expiry': 10})

    data = response.json()
    return data['data']['token']


def setup_user():
    response = requests.post(f'{BASE_URL}/auth/register', json={
        'token': generate_token(),
        'name': 'fixture_user',
        'password': 'test_password'
    })
    print(response.json())
    return response.json()['data']['user_id']


response = requests.patch(f'{BASE_URL}/auth/unset_admin', headers={
        'Authorization': f'Bearer {access}'
    }, json={'user_id': setup_user(), 'admin_key': 'changeme'})
data = response.json()

print(data)
"""
# Отправка POST-запроса
response = requests.post(url, json=data, headers=headers)

# Проверка статуса ответа и вывод результата
if response.status_code == 201:
    print('Token created successfully')
    print('Response:', response.json())
else:
    print('Status code:', response.status_code)
    print('Response:', response.json())

# URL вашего сервиса
url = 'http://127.0.0.1:5000/auth/get_tokens'

# Отправка POST-запроса
response = requests.get(url)

# Проверка статуса ответа и вывод результата
if response.status_code == 200:
    print('Token update expire successfully')
    print('Response:', response.json()["data"])
else:
    print('Response:', response.json())


Response: {'data': [{'created_at': '2024-08-07T15:22:23.127140', 'expiry_date': 'Fri, 06 Sep 2024 15:22:23 GMT', 'token': 'b28180e7-9528-4c83-b763-6ce97e0f4051'},
 {'created_at': '2024-08-07T15:24:59.969836',
  'expiry_date': 'Fri, 06 Sep 2024 15:24:59 GMT',
   'token': 'fa35ec4b-e415-4daf-ac40-886cafed99af'}, 
{'created_at': '2024-08-08T05:14:33.080297', 
'expiry_date': 'Sat, 07 Sep 2024 05:14:33 GMT', 
'token': '3ad208f8-67db-48d9-9037-f43af036fc32'}], 
'message': 'Tokens retrieved successfully'}


url = 'http://localhost:5050/auth/get_tokens'


# Отправка GET-запроса
print(requests.get(url))
response = requests.get(url)
# Проверка статуса ответа и вывод результата
if response.status_code == 200:
    print("Response:", response.json()["message"])
    print('Response:', response.json())
else:
    print('Failed to get token')
    print('Status code:', response.status_code)
    print('Response:', response.json())

url = 'http://localhost:5000/auth/delete_expired_token'


# Отправка GET-запроса
response = requests.delete(url)

# Проверка статуса ответа и вывод результата
if response.status_code == 200:
    print("Response:", response.json()["message"])
    print('Response:', response.json())
else:
    print('Failed to delete token')
    print('Status code:', response.status_code)
    print('Response:', response.json)

url = 'http://localhost:5000/auth/set_max_users'

body = {
    "token": '78126743-b1ee-4f6c-85ba-637396ad3869',
    'max_users': 10
}

# Отправка GET-запроса
response = requests.patch(url, json=body)

# Проверка статуса ответа и вывод результата
if response.status_code == 201:
    print("Response:", response.json()["message"])
    print('Response:', response.json())
else:
    print('Failed to set max users token')
    print('Status code:', response.status_code)
    print('Response:', response.json())

print("\n некст \n")

url = 'http://localhost:5000/auth/get_tokens'

# Отправка GET-запроса
response = requests.get(url)

# Проверка статуса ответа и вывод результата
if response.status_code == 200:
    print("Response:", response.json()["message"])
    print('Response:', response.json())
else:
    print('Failed to get token')
    print('Status code:', response.status_code)
    print('Response:', response.json())

# URL вашего сервиса
url = 'http://127.0.0.1:5000/auth/login'

body = {
    "name": "Trighty",
    "password": "FIRST",
}

# Отправка POST-запроса
response = requests.post(url, json=body)

# Проверка статуса ответа и вывод результата
if response.status_code == 201:
    print('Login user successfully')
    print('Response:', response.json())
else:
    print('Failed to login user')
    print('Status code:', response.status_code)
    print('Response:', response.json())"""