from conftest import *


def test_generate_token(admin_token):
    response = requests.post(f'{BASE_URL}/auth/generate_token', headers={
        'Authorization': f'Bearer {admin_token}'
    }, json={'expiry': 10})

    assert response.status_code == 201
    data = response.json()
    assert 'token' in data['data']
    assert 'expiry_date' in data['data']


def test_update_token_expiry(admin_token, setup_token):
    # Используем токен из фикстуры setup_tokens
    token = setup_token

    # Затем обновляем его
    response = requests.patch(f'{BASE_URL}/auth/update_token_expiry', headers={
        'Authorization': f'Bearer {admin_token}'
    }, json={'token': token, 'expiry': 10})

    assert response.status_code == 201
    data = response.json()
    assert 'expiry_date' in data['data']


def test_get_tokens(admin_token):
    response = requests.get(f'{BASE_URL}/auth/get_tokens', headers={
        'Authorization': f'Bearer {admin_token}'
    })

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data['data'], list)


def test_delete_expired_token(admin_token):
    response = requests.delete(f'{BASE_URL}/auth/delete_expired_token', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    assert response.status_code == 200


def test_delete_token(admin_token, setup_token):
    # Используем токен из фикстуры setup_tokens
    token = setup_token

    # Затем удаляем его
    response = requests.delete(f'{BASE_URL}/auth/delete_token', headers={
        'Authorization': f'Bearer {admin_token}'
    }, json={'token': token})

    assert response.status_code == 200


def test_set_max_users(admin_token, setup_token):
    token = setup_token  # Используем токен из фикстуры

    response = requests.patch(f'{BASE_URL}/auth/set_max_users', headers={
        'Authorization': f'Bearer {admin_token}'
    }, json={'token': token, 'max_users': 50})

    assert response.status_code == 201
    data = response.json()
    assert data['data']['max_users'] == 50


