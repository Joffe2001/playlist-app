from flask import Blueprint, request, render_template, flash, redirect, session, jsonify, send_file
from .models import User, fs
from io import BytesIO
from bson import ObjectId


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

view_bp = Blueprint('views', __name__)

@view_bp.route('/')
def index():
    return render_template('index.html', user=session.get('username'))

@view_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if not all([username, email, password, first_name, last_name]):
            flash("Missing required fields", 'error')
            return redirect('/register?error=missing_fields')

        existing_user = User.find_by_username(username=username)
        if existing_user:
            flash("Username already exists", 'error')
            return redirect('/register?error=username_exists')

        user = User(username, email, password, first_name, last_name)

        try:
            user.save()
            flash(f"Welcome {username}, you've successfully registered!", 'success')
            session['username'] = user.username
            return redirect(f'/{username}/profile')

        except Exception as e:
            print(f"Error saving user: {e}")
            flash("User registration failed. Please try again.", 'error')
            return redirect('/register')

    else:
        return render_template('register.html')

@view_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')

        if not all([username, password]):
            return redirect('/login?error=missing_fields')

        user = User.login_user(username, password)

        if user is None:
            return redirect('/login?error=invalid_input')

        session['username'] = user.username
        flash("Login successful", 'success')
        return redirect(f'/{username}/profile')

    else:
        return render_template('login.html')

@view_bp.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    flash("Logged out successfully", 'success')
    return redirect('/')

@view_bp.route('/<username>/profile', methods=['GET', 'POST'])
def profile(username):
    current_user = session.get('username')
    user = User.find_by_username(username=username)

    if not user:
        flash("User not found", 'error')
        return redirect('/')

    return render_template('profile.html', user=user, current_user=current_user)

@view_bp.route('/edit_bio', methods=['POST'])
def edit_bio():
    current_username = session.get('username')
    new_bio = request.json.get('bio')

    if current_username:
        user = User.find_by_username(current_username)
        if user:
            user.update_bio(new_bio)
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'error': 'User not found'}), 404
    else:
        return jsonify({'success': False, 'error': 'User not authenticated'}), 401


@view_bp.route('/profile_pic/<file_id>')
def profile_pic(file_id):
    try:
        file_id = ObjectId(file_id)
        file = fs.get(file_id)
        if file:
            response = send_file(BytesIO(file.read()), mimetype=file.content_type)
            return response
        else:
            return 'File not found', 404
    except Exception as e:
        print(f"Error retrieving profile picture: {e}")
        return 'Error retrieving profile picture', 500
    
@view_bp.route('/upload_pic', methods=['POST'])
def upload_pic():
    current_user = session.get('username')
    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file and allowed_file(file.filename):
            file_data = file.read()
            file_id = fs.put(file_data, filename=file.filename, content_type=file.content_type)
            if current_user:
                user = User.find_by_username(current_user)
                if user:
                    user.update_profile_pic(file_id)
                    return jsonify({'success': True}), 200
                else:
                    return jsonify({'success': False, 'error': 'User not found'}), 404
            else:
                return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        else:
            return jsonify({'success': False, 'error': 'Invalid file format'}), 400
    else:
        return jsonify({'success': False, 'error': 'No file part'}), 400

@view_bp.route('/follow', methods=['POST'])
def follow_user():
    try:
        data = request.json
        following_username = data.get('following_username')
        current_username = session.get('username')

        if not current_username:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401

        # Find the user to follow
        following_user = User.find_by_username(following_username)

        if not following_user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        # Perform the follow action
        current_user = User.find_by_username(current_username)
        current_user.add_following(following_username)
        following_user.add_follower(current_username)

        return jsonify({'success': True, 'message': f'You are now following {following_username}'}), 200

    except Exception as e:
        print(f"Error following user: {e}")
        return jsonify({'success': False, 'error': 'An error occurred while following user'}), 500
    
@view_bp.route('/unfollow', methods=['POST'])
def unfollow_user():
    try:
        data = request.json
        following_username = data.get('following_username')
        current_username = session.get('username')

        if not current_username:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401

        # Find the user to unfollow
        following_user = User.find_by_username(following_username)

        if not following_user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        # Perform the unfollow action
        current_user = User.find_by_username(current_username)
        current_user.remove_following(following_username)
        following_user.remove_follower(current_username)

        return jsonify({'success': True, 'message': f'You have unfollowed {following_username}'}), 200

    except Exception as e:
        print(f"Error unfollowing user: {e}")
        return jsonify({'success': False, 'error': 'An error occurred while unfollowing user'}), 500

@view_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({"message": "Unauthorized access"}), 401