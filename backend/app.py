from flask import Flask
from users_profile.views import view_bp
from users_playlist.views import user_playlist_bp
import os

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend/templates')
app.config["SECRET_KEY"] = os.urandom(24)

# Register Blueprint
app.register_blueprint(view_bp, url_prefix='/')
app.register_blueprint(user_playlist_bp, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)