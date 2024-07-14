import pytest
from flask import Flask
from backend.users_profile.views import view_bp
from backend.users_playlist.views import user_playlist_bp
import os

@pytest.fixture
def client():
    """Create and configure a test client for the app."""
    app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend/templates')
    app.config["SECRET_KEY"] = os.urandom(24)
    app.register_blueprint(view_bp, url_prefix='/')
    app.register_blueprint(user_playlist_bp, url_prefix='/')

    with app.test_client() as client:
        yield client

def test_index(client):
    """Test if the index route returns a 200 status code."""
    response = client.get('/')
    assert response.status_code == 200

# Add more test functions as needed

if __name__ == '__main__':
    pytest.main()