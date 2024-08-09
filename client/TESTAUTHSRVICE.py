import requests
"""
# URL вашего сервиса
url = 'http://localhost:5000/auth/generate_token'
headers = {'Content-Type': 'application/json'}

data = {
    'expiry': 30
}

# Отправка POST-запроса
response = requests.post(url, json=data, headers=headers)

# Проверка статуса ответа и вывод результата
if response.status_code == 201:
    print('Token created successfully')
    print('Response:', response.json())
else:
    print('Failed to create token')
    print('Status code:', response.status_code)
    print('Response:', response.json())


# URL вашего сервиса
url = 'http://localhost:5000/auth/update_token'
headers = {'Content-Type': 'application/json'}

data = {
    'token': "3ad208f8-67db-48d9-9037-f43af036fc32",
    'expiry': 900
}

# Отправка POST-запроса
response = requests.patch(url, json=data, headers=headers)

# Проверка статуса ответа и вывод результата
if response.status_code == 201:
    print('Token update expire successfully')
    print('Response:', response.json())
else:
    print('Failed to update token expire')
    print('Status code:', response.status_code)
    print('Response:', response.json())


Response: {'data': [{'created_at': '2024-08-07T15:22:23.127140', 'expiry_date': 'Fri, 06 Sep 2024 15:22:23 GMT', 'token': 'b28180e7-9528-4c83-b763-6ce97e0f4051'},
 {'created_at': '2024-08-07T15:24:59.969836',
  'expiry_date': 'Fri, 06 Sep 2024 15:24:59 GMT',
   'token': 'fa35ec4b-e415-4daf-ac40-886cafed99af'}, 
{'created_at': '2024-08-08T05:14:33.080297', 
'expiry_date': 'Sat, 07 Sep 2024 05:14:33 GMT', 
'token': '3ad208f8-67db-48d9-9037-f43af036fc32'}], 
'message': 'Tokens retrieved successfully'}
"""


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

print("\n некст \n")
"""
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

"""

url = 'http://localhost:5000/auth/set_max_users'

body = {
    "token": '92fc459a-e301-4c6c-86e0-4ecab5d9db82',
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
