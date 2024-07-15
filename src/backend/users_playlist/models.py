from pymongo import MongoClient
import pymongo
from users_profile.models import User, db, user_collection

playlist_collection = db["playlists"]

class Playlist:
    PLATFORMS = ['spotify', 'youtube', 'apple']

    def __init__(self, name, creator_username, platform, music_link):
        self.name = name
        self.creator_username = creator_username
        self.platform = platform
        self.music_link = music_link

    def save(self):
        playlist_data = {
            "name": self.name,
            "creator_username": self.creator_username,
            "platform": self.platform,
            "music_link": self.music_link
        }
        try:
            playlist_collection.insert_one(playlist_data)
        except pymongo.errors.PyMongoError as e:
            print(f"Error saving playlist: {e}")

    @classmethod
    def find_by_name(cls, name):
        playlist_data = playlist_collection.find_one({"name": name})
        if playlist_data:
            creator_username = playlist_data["creator_username"]
            creator_user = User.find_by_username(creator_username)
            if creator_user:
                playlist_data["creator_username"] = {
                    "username": creator_user.username,
                    "email": creator_user.email
                }
            return Playlist(
                name=playlist_data["name"],
                creator_username=playlist_data["creator_username"],
                platform=playlist_data["platform"],
                music_link=playlist_data["music_link"],
            )
        else:
            return None

    @classmethod
    def add_playlist(cls, name, creator_username, platform, music_link):
        # Validate link if needed before saving
        if platform not in cls.PLATFORMS:
            raise ValueError("Invalid platform")

        # Validate the link based on the selected platform
        if platform == 'spotify' and not cls.validate_spotify_link(music_link):
            raise ValueError("Invalid Spotify link format")
        elif platform == 'youtube' and not cls.validate_youtube_music_link(music_link):
            raise ValueError("Invalid YouTube Music link format")
        elif platform == 'apple' and not cls.validate_apple_music_link(music_link):
            raise ValueError("Invalid Apple Music link format")

        playlist = Playlist(name, creator_username, platform, music_link)
        playlist.save()

        user = User.find_by_username(creator_username)
        if user:
            user.my_playlists.append(name)
            user.save()
        else:
            print(f"User {creator_username} not found.")

        return playlist

    @classmethod
    def delete_playlist(cls, name, username):
        try:
            result = playlist_collection.delete_one({"name": name, "creator_username": username})
            if result.deleted_count > 0:
                user = User.find_by_username(username)
                if user and name in user.my_playlists:
                    user.my_playlists.remove(name)
                    user.save()
                return True
            return False
        except pymongo.errors.PyMongoError as e:
            print(f"Error deleting playlist: {e}")
            return False

    @classmethod
    def find_random_playlists(cls, count=10):
        try:
            pipeline = [{'$sample': {'size': count}}]
            random_playlists = list(playlist_collection.aggregate(pipeline))
            return [cls(
                name=playlist["name"],
                creator_username=playlist["creator_username"],
                platform=playlist["platform"],
                music_link=playlist["music_link"]
            ) for playlist in random_playlists]
        except pymongo.errors.PyMongoError as e:
            print(f"Error retrieving random playlists: {e}")
            return []

    @staticmethod
    def validate_spotify_link(link):
        return link.startswith('https://open.spotify.com/playlist/')

    @staticmethod
    def validate_youtube_music_link(link):
        return link.startswith('https://music.youtube.com/playlist?')

    @staticmethod
    def validate_apple_music_link(link):
        return link.startswith('https://music.apple.com/')
