import pytest
from unittest.mock import patch
from backend.app import app
from backend.users_playlist.models import User, Playlist

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('backend.users_playlist.views.User')
@patch('backend.users_playlist.views.Playlist')
def test_add_playlist(mock_playlist, mock_user, client):
    mock_user.find_by_username.return_value = mock_user
    mock_playlist.add_playlist.return_value = mock_playlist

    with client.session_transaction() as sess:
        sess['username'] = 'testuser'

    response = client.post('/add_playlist', json={
        'playlist_name': 'Test Playlist',
        'platform': 'spotify',
        'music_link': 'https://open.spotify.com/playlist/test'
    })

    assert response.status_code == 200
    assert b"Playlist added successfully" in response.data

@patch('backend.users_playlist.views.User')
@patch('backend.users_playlist.views.Playlist')
def test_delete_playlist(mock_playlist, mock_user, client):
    mock_user.find_by_username.return_value = mock_user
    mock_playlist.delete_playlist.return_value = True

    with client.session_transaction() as sess:
        sess['username'] = 'testuser'

    response = client.post('/delete_playlist', json={
        'playlist_name': 'Test Playlist'
    })

    assert response.status_code == 200
    assert b"Playlist deleted successfully" in response.data

@patch('backend.users_playlist.views.playlist_collection')
def test_get_playlists(mock_collection, client):
    mock_collection.find.return_value = [{'name': 'Test Playlist', 'creator_username': 'testuser', 'platform': 'spotify', 'music_link': 'https://open.spotify.com/playlist/test'}]

    response = client.get('/get_playlists?username=testuser')

    assert response.status_code == 200
    assert b'Test Playlist' in response.data

@patch('backend.users_playlist.views.User')
@patch('backend.users_playlist.views.Playlist')
def test_user_playlists(mock_playlist, mock_user, client):
    mock_user.find_by_username.return_value = mock_user
    mock_user.my_playlists = ['Test Playlist']
    mock_playlist.find_by_name.return_value = mock_playlist

    response = client.get('/testuser/playlists')

    assert response.status_code == 200
    assert b'Test Playlist' in response.data

def test_unauthorized_handler(client):
    response = client.get('/unauthorized')
    assert response.status_code == 401
    assert b'Unauthorized access' in response.data