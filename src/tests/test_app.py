import pytest
from flask import url_for
from backend.app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_index_page(client):
    response = client.get(url_for('views.index'))
    assert response.status_code == 200
    assert b'Welcome to Ido\'s Project' in response.data

def test_register_page(client):
    response = client.get(url_for('views.register'))
    assert response.status_code == 200
    assert b'Register' in response.data

def test_login_page(client):
    response = client.get(url_for('views.login'))
    assert response.status_code == 200
    assert b'Login' in response.data

def test_profile_page(client):
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    response = client.get(url_for('views.profile', username='testuser'))
    assert response.status_code == 200
    assert b'Profile' in response.data
    assert b'testuser' in response.data

def test_user_playlists_page(client):
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    response = client.get(url_for('users_playlist.user_playlists', username='testuser'))
    assert response.status_code == 200
    assert b'testuser\'s Playlists' in response.data