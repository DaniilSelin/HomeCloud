from conftest import *
import uuid


def test_register_user(setup_token):
    token = setup_token  # Используем токен из фикстуры

    response = requests.post(f'{BASE_URL}/auth/register', json={
        'token': token,
        'name': 'test_user',
        'password': 'test_password'
    })

    assert response.status_code == 201
    data = response.json()
    assert data['data']['user_name'] == 'test_user'


def test_login_user():
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'name': 'test_user',
        'password': 'test_password'
    })

    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data['data']


def test_get_users(admin_token):
    response = requests.get(f'{BASE_URL}/auth/get_users', headers={
        'Authorization': f'Bearer {admin_token}'
    })

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data['data'], list)


@pytest.mark.parametrize('setup_user', [
    f'test_get_user_by_id"'
], indirect=True)
def test_get_user_by_id(admin_token, setup_user):
    response = requests.get(f'{BASE_URL}/auth/get_user_by_id', headers={
        'Authorization': f'Bearer {admin_token}'
    }, params={'user_id': setup_user["user_id"]})

    assert response.status_code == 200
    data = response.json()
    assert 'user_id' in data['data']


def test_get_user_by_name(admin_token):
    response = requests.get(f'{BASE_URL}/auth/get_user_by_name', headers={
        'Authorization': f'Bearer {admin_token}'
    }, params={'user_name': 'test_user'})

    assert response.status_code == 200
    data = response.json()
    assert data['data']['user_name'] == 'test_user'


def test_change_password(admin_token):
    response = requests.patch(f'{BASE_URL}/auth/change_password', headers={
        'Authorization': f'Bearer {admin_token}'
    }, json={'new_password': 'changeme'})

    assert response.status_code == 201


def test_update_name_user(admin_token):
    response = requests.patch(f'{BASE_URL}/auth/update_user', headers={
        'Authorization': f'Bearer {admin_token}'
    }, json={'new_name': 'homeuser'})

    assert response.status_code == 201


@pytest.mark.parametrize('setup_user', [
    f'test_set_admin'
], indirect=True)
def test_set_admin(admin_token, setup_user):
    response = requests.patch(f'{BASE_URL}/auth/set_admin', headers={
        'Authorization': f'Bearer {admin_token}'
    }, json={'user_id': setup_user["user_id"], 'admin_key': 'changeme'})

    assert response.status_code == 201


@pytest.mark.parametrize('setup_user', [
    f'test_unset_admin'
], indirect=True)
def test_unset_admin(admin_token, setup_user):
    response = requests.patch(f'{BASE_URL}/auth/unset_admin', headers={
        'Authorization': f'Bearer {admin_token}'
    }, json={'user_id': setup_user["user_id"], 'admin_key': 'changeme'})

    assert response.status_code == 201
