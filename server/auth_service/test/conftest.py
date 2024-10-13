import pytest
import requests

# ЗАМЕНИ БАЩОВЫЙ НА 127.0.0.1 если тесты на месте проводить хочешь
BASE_URL = 'http://auth_service:5000'


@pytest.fixture(scope='function')
def admin_token():
    # Получаем токен администратора (может потребоваться регистрация или создание токена)
    response = requests.post(BASE_URL + '/auth/login', json={
        'name': 'homeuser',
        'password': 'changeme'
    })
    assert response.status_code == 200
    data = response.json()
    return data['data']['access_token']


@pytest.fixture(scope='function')
def setup_token(admin_token):
    # Создаем токен для тестирования
    response = requests.post(f'{BASE_URL}/auth/generate_token', headers={
        'Authorization': f'Bearer {admin_token}'
    }, json={'expiry': 10})
    assert response.status_code == 201
    return response.json()['data']['token']


@pytest.fixture(scope="function")
def setup_user(request, setup_token):
    # Получаем имя пользователя из параметра или создаем уникальное
    user_name = request.param if hasattr(request, 'param') else f'fixture_user'

    response = requests.post(f'{BASE_URL}/auth/register', json={
        'token': setup_token,
        'name': user_name,
        'password': 'test_password'
    })
    assert response.status_code == 201
    return response.json()['data']


@pytest.fixture(scope='function')
def cleanup_tokens(admin_token):
    # Очищаем токены перед началом тестов
    response = requests.delete(BASE_URL + '/auth/delete_expired_token', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    assert response.status_code == 200


@pytest.fixture(scope='function')
def get_tokens(admin_token):
    response = requests.get(f'{BASE_URL}/auth/get_tokens', headers={
        'Authorization': f'Bearer {admin_token}'
    })

    assert response.status_code == 200
    data = response.json()
    return data['data']