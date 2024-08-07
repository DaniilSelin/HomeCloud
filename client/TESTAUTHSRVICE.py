import requests
"""
# URL вашего сервиса
url = 'http://localhost:5000/auth/generate_token'
headers = {'Content-Type': 'application/json'}

data = {
    'expiry_days': 30
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
"""
url = 'http://localhost:5000/auth/get_tokens'


# Отправка GET-запроса
response = requests.get(url)

# Проверка статуса ответа и вывод результата
if response.status_code == 200:
    print('Response:', response.json())
else:
    print('Failed to get token')
    print('Status code:', response.status_code)
    print('Response:', response.json)