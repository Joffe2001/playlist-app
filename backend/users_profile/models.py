from pymongo import MongoClient
import pymongo
from passlib.context import CryptContext
import re
from flask_login import UserMixin
from gridfs import GridFS

# MongoDB setup
try:
    client = MongoClient("mongodb://root:rootpassword@mongodb_users:27017/")
    db = client["project"]
    user_collection = db["users"]
    playlist_collection = db["playlists"]
    fs = GridFS(db)
except pymongo.errors.ConnectionFailure as e:
    print("Connection failed:", e)

# Password hashing setup
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Username validation regex
USERNAME_REGEX = re.compile(r'^\w+$')

class User(UserMixin):
    def __init__(self, username, email, password, first_name, last_name, is_active=False):
        self.username = username
        self.email = email
        self.hashed_password = self._hash_password(password) if password else None
        self.first_name = first_name
        self.last_name = last_name
        self.is_active = is_active
        self.my_playlists = []
        self.followers = [] 
        self.following = []
        self.liked_playlists = []
        self.bio = None
        self.profile_pic = None

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        self._is_active = value

    def _hash_password(self, password):
        return pwd_context.hash(password)

    def save(self):
        user_data = {
            "email": self.email,
            "is_active": self.is_active,
            "my_playlists": self.my_playlists,
            "followers": self.followers, 
            "following": self.following,
            "liked_playlists": self.liked_playlists,
            "bio": self.bio,
            "profile_pic": self.profile_pic
        }

        # Only include hashed_password, first_name, and last_name if they are set
        if self.hashed_password:
            user_data["hashed_password"] = self.hashed_password
        if self.first_name:
            user_data["first_name"] = self.first_name
        if self.last_name:
            user_data["last_name"] = self.last_name

        existing_user = user_collection.find_one({"username": self.username})
        if existing_user:
            user_collection.update_one({"username": self.username}, {"$set": user_data})
        else:
            # Ensure username is always included in the document
            user_data["username"] = self.username
            user_collection.insert_one(user_data)


    def update_bio(self, new_bio):
        self.bio = new_bio
        update_fields = {
            "bio": self.bio
        }
        user_collection.update_one({"username": self.username}, {"$set": update_fields})

    
    def add_following(self, following_username):
        if following_username not in self.following:
            self.following.append(following_username)
            update_fields = {
            "following": self.following
        }
        user_collection.update_one({"username": self.username}, {"$set": update_fields})
    
    def add_follower(self, follower_username):
        if follower_username not in self.followers:
            self.followers.append(follower_username)
            update_fields = {
            "followers": self.followers
        }
        user_collection.update_one({"username": self.username}, {"$set": update_fields})

    def remove_following(self, following_username):
        if following_username in self.following:
            self.following.remove(following_username)
            update_fields = {
            "following": self.following
        }
        user_collection.update_one({"username": self.username}, {"$set": update_fields})

    def remove_follower(self, follower_username):
        if follower_username not in self.followers:
            self.followers.remove(follower_username)
            update_fields = {
            "followers": self.followers
        }
        user_collection.update_one({"username": self.username}, {"$set": update_fields})


    def update_profile_pic(self, filename):
        self.profile_pic = filename
        update_fields = {
            "profile_pic": self.profile_pic
        }
        user_collection.update_one({"username": self.username}, {"$set": update_fields})

    @property
    def followers_count(self):
        return len(self.followers)

    @property
    def following_count(self):
        return len(self.following)

    @classmethod
    def get_followers(cls, username):
        user = user_collection.find_one({"username": username}, {"followers": 1, "_id": 0})
        if user and 'followers' in user:
            return user['followers']
        return []

    @classmethod
    def find_by_username(cls, username):
        user_data = user_collection.find_one({"username": username})
        if user_data:
            user = User(
                user_data["username"],
                user_data["email"],
                None, None, None,
                user_data.get("is_active", False)
            )
            user.my_playlists = user_data.get("my_playlists", [])
            user.followers = user_data.get("followers", [])  # Load followers from user document
            user.following = user_data.get("following", [])
            user.liked_playlists = user_data.get("liked_playlists", [])
            user.bio = user_data.get("bio", None)
            user.profile_pic = user_data.get("profile_pic", None)
            return user
        else:
            return None

    @classmethod
    def login_user(cls, username, password):
        user = cls.find_by_username(username)
        if user:
            hashed_password = user_collection.find_one({"username": username})["hashed_password"]
            if pwd_context.verify(password, hashed_password):
                return user
        return None