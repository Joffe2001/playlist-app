import pytest

class Playlist:
    PLATFORMS = ['spotify', 'youtube', 'apple']

    def __init__(self, name, creator_username, platform, music_link):
        self.name = name
        self.creator_username = creator_username
        self.platform = platform
        self.music_link = music_link

    @staticmethod
    def validate_spotify_link(link):
        return link.startswith('https://open.spotify.com/playlist/')

    @staticmethod
    def validate_youtube_music_link(link):
        return link.startswith('https://music.youtube.com/playlist?')

    @staticmethod
    def validate_apple_music_link(link):
        return link.startswith('https://music.apple.com/') and 'playlist' in link

    @classmethod
    def add_playlist(cls, name, creator_username, platform, music_link):
        if platform not in cls.PLATFORMS:
            raise ValueError("Invalid platform")

        if platform == 'spotify' and not cls.validate_spotify_link(music_link):
            raise ValueError("Invalid Spotify link format")
        elif platform == 'youtube' and not cls.validate_youtube_music_link(music_link):
            raise ValueError("Invalid YouTube Music link format")
        elif platform == 'apple' and not cls.validate_apple_music_link(music_link):
            raise ValueError("Invalid Apple Music link format")

        return cls(name, creator_username, platform, music_link)


def test_validate_spotify_link():
    assert Playlist.validate_spotify_link('https://open.spotify.com/playlist/1234567890')
    assert not Playlist.validate_spotify_link('https://open.spotify.com/album/1234567890')


def test_validate_youtube_music_link():
    assert Playlist.validate_youtube_music_link('https://music.youtube.com/playlist?list=PL1234567890')
    assert not Playlist.validate_youtube_music_link('https://music.youtube.com/watch?v=1234567890')


def test_validate_apple_music_link():
    assert Playlist.validate_apple_music_link('https://music.apple.com/us/playlist/1234567890')
    assert not Playlist.validate_apple_music_link('https://music.apple.com/us/album/1234567890')


def test_add_playlist_valid():
    playlist = Playlist.add_playlist('My Playlist', 'existing_user', 'spotify', 'https://open.spotify.com/playlist/1234567890')
    assert playlist.name == 'My Playlist'
    assert playlist.creator_username == 'existing_user'
    assert playlist.platform == 'spotify'
    assert playlist.music_link == 'https://open.spotify.com/playlist/1234567890'


def test_add_playlist_invalid_platform():
    with pytest.raises(ValueError, match="Invalid platform"):
        Playlist.add_playlist('My Playlist', 'existing_user', 'invalid_platform', 'https://open.spotify.com/playlist/1234567890')


def test_add_playlist_invalid_link():
    with pytest.raises(ValueError, match="Invalid Spotify link format"):
        Playlist.add_playlist('My Playlist', 'existing_user', 'spotify', 'https://open.spotify.com/album/1234567890')

    with pytest.raises(ValueError, match="Invalid YouTube Music link format"):
        Playlist.add_playlist('My Playlist', 'existing_user', 'youtube', 'https://music.youtube.com/watch?v=1234567890')

    with pytest.raises(ValueError, match="Invalid Apple Music link format"):
        Playlist.add_playlist('My Playlist', 'existing_user', 'apple', 'https://music.apple.com/us/album/1234567890')