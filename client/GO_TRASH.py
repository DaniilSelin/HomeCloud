import requests

BASE_URL = 'http://localhost:8000'
response = requests.post(BASE_URL + '/')

print(response.text)