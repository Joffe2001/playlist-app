from flask import Blueprint, request, render_template, flash, redirect, session, jsonify
from .models import User, Playlist, playlist_collection

user_playlist_bp = Blueprint('users_playlist', __name__)


@user_playlist_bp.route('/add_playlist', methods=['POST'])
def add_playlist():
    username = session.get('username')  

    if not username:
        flash("Unauthorized access", 'error')
        return jsonify({"message": "Unauthorized access"}), 401

    data = request.json
    playlist_name = data.get('playlist_name')
    platform = data.get('platform')
    music_link = data.get('music_link')

    if not playlist_name or not platform or not music_link:
        flash("Please fill in all required fields", 'error')
        return jsonify({"message": "Please fill in all required fields"}), 400

    user = User.find_by_username(username)
    if not user:
        flash("User not found", 'error')
        return jsonify({"message": "User not found"}), 404

    try:
        playlist = Playlist.add_playlist(
            name=playlist_name,
            creator_username=username, 
            platform=platform,
            music_link=music_link
        )
        flash(f"Playlist '{playlist_name}' created successfully", 'success')
        return jsonify({"message": "Playlist added successfully", "username": username}), 200
    except ValueError as e:
        flash(str(e), 'error')
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        flash("Error adding playlist", 'error')
        return jsonify({"message": "Error adding playlist"}), 500

@user_playlist_bp.route('/delete_playlist', methods=['POST'])
def delete_playlist():
    username = session.get('username')

    if not username:
        return jsonify({"message": "Unauthorized access"}), 401

    data = request.json
    playlist_name = data.get('playlist_name')

    if not playlist_name:
        return jsonify({"message": "Playlist name is required"}), 400

    success = Playlist.delete_playlist(playlist_name, username)

    if success:
        return jsonify({"message": "Playlist deleted successfully"}), 200
    else:
        return jsonify({"message": "Error deleting playlist"}), 500

@user_playlist_bp.route('/get_playlists', methods=['GET'])
def get_playlists():
    username = request.args.get('username')  # Fetch username from query parameter
    
    if not username:
        return jsonify({"error": "Username parameter is required"}), 400

    playlists = list(playlist_collection.find({"creator_username": username}))
    if not playlists:
        return jsonify({"message": "No playlists found for this user"}), 404

    return jsonify(playlists), 200

@user_playlist_bp.route('/<username>/playlists', methods=['GET'])
def user_playlists(username):
    user = User.find_by_username(username)

    if not user:
        flash("User not found", 'error')
        return redirect('/')

    playlists = []
    for playlist_name in user.my_playlists:
        playlist = Playlist.find_by_name(playlist_name)
        if playlist:
            playlists.append(playlist)

    return render_template('user_playlists.html', user=user, playlists=playlists)

@user_playlist_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({"message": "Unauthorized access"}), 401