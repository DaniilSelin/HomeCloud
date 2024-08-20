import pytest
import requests


BASE_URL = 'http://127.0.0.1:5000'


@pytest.fixture(scope='module')
def admin_token():
    # Здесь предполагается, что ваш сервер уже запущен.
    # Получаем токен администратора (может потребоваться регистрация или создание токена)
    response = requests.post(BASE_URL + '/auth/login', json={
        'name': 'homeuser',
        'password': 'changeme'
    })
    assert response.status_code == 200
    data = response.json()
    return data['data']['access_token']


@pytest.fixture(scope='module')
def setup_tokens(admin_token):
    # Создаем токен для тестирования
    response = requests.post(BASE_URL + '/auth/generate_token', headers={
        'Authorization': f'Bearer {admin_token}'
    }, json={'expiry': 10})
    assert response.status_code == 201
    return response.json()['data']['token']


@pytest.fixture(scope='module')
def cleanup_tokens(admin_token):
    # Очищаем токены перед началом тестов
    response = requests.delete(BASE_URL + '/auth/delete_expired_token', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    assert response.status_code == 200