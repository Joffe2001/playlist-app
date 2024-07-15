import pytest
from io import BytesIO
from unittest.mock import patch
from backend.app import app
from backend.users_profile.models import User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('backend.users_profile.views.User')
def test_index(mock_user, client):
    mock_user.return_value.find_random_playlists.return_value = []
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome' in response.data

@patch('backend.users_profile.views.User')
def test_register_get(mock_user, client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data

@patch('backend.users_profile.views.User')
def test_register_post(mock_user, client):
    mock_user.return_value.find_by_username.return_value = None
    mock_user.return_value.save.return_value = None

    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password',
        'first_name': 'Test',
        'last_name': 'User'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Welcome testuser' in response.data

@patch('backend.users_profile.views.User')
def test_login_get(mock_user, client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

@patch('backend.users_profile.views.User')
def test_login_post(mock_user, client):
    mock_user.return_value.login_user.return_value = mock_user
    mock_user.username = 'testuser'

    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Login successful' in response.data

def test_logout(client):
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Logged out successfully' in response.data

@patch('backend.users_profile.views.User')
def test_profile(mock_user, client):
    mock_user.return_value.find_by_username.return_value = mock_user
    mock_user.username = 'testuser'

    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    response = client.get('/testuser/profile')
    assert response.status_code == 200
    assert b'testuser' in response.data

@patch('backend.users_profile.views.User')
def test_edit_bio(mock_user, client):
    mock_user.return_value.find_by_username.return_value = mock_user

    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    response = client.post('/edit_bio', json={'bio': 'New bio'})
    assert response.status_code == 200
    assert response.json['success'] == True

@patch('backend.users_profile.views.fs')
def test_profile_pic(mock_fs, client):
    mock_fs.get.return_value.read.return_value = b'fakeimage'
    mock_fs.get.return_value.content_type = 'image/png'

    response = client.get('/profile_pic/507f191e810c19729de860ea')
    assert response.status_code == 200
    assert response.content_type == 'image/png'

@patch('backend.users_profile.views.User')
@patch('backend.users_profile.views.fs')
def test_upload_pic(mock_fs, mock_user, client):
    mock_user.return_value.find_by_username.return_value = mock_user

    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    data = {
        'profile_pic': (BytesIO(b'test_image_content'), 'test_image.png')
    }

    response = client.post('/upload_pic', content_type='multipart/form-data', data=data)
    assert response.status_code == 200
    assert response.json['success'] == True

@patch('backend.users_profile.views.User')
def test_follow_user(mock_user, client):
    mock_user.return_value.find_by_username.side_effect = [mock_user, mock_user]

    with client.session_transaction() as sess:
        sess['username'] = 'testuser'

    response = client.post('/follow', json={'following_username': 'anotheruser'})
    assert response.status_code == 200
    assert response.json['success'] == True

@patch('backend.users_profile.views.User')
def test_unfollow_user(mock_user, client):
    mock_user.return_value.find_by_username.side_effect = [mock_user, mock_user]

    with client.session_transaction() as sess:
        sess['username'] = 'testuser'

    response = client.post('/unfollow', json={'following_username': 'anotheruser'})
    assert response.status_code == 200
    assert response.json['success'] == True

def test_easteregg(client):
    response = client.get('/easteregg')
    assert response.status_code == 200
    assert b'Easter Egg' in response.data