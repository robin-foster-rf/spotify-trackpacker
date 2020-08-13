import spotipy
from spotipy.oauth2 import SpotifyOAuth
from uuid import uuid4

from config import SpotifyConfig as Keys

scope = ' '.join([
    'user-read-playback-state', 
    'user-modify-playback-state', 
    'user-read-currently-playing', 
    'streaming', 
    'app-remote-control', 
    'user-read-email', 
    'user-read-private', 
    'playlist-read-collaborative', 
    'playlist-modify-public', 
    'playlist-read-private', 
    'playlist-modify-private', 
    'user-library-modify', 
    'user-library-read', 
    'user-top-read', 
    'user-read-playback-position', 
    'user-read-recently-played',
])

def init_spotify():
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=Keys.CLIENT_ID, 
            client_secret=Keys.CLIENT_SECRET, 
            redirect_uri=Keys.REDIRECT_URI,
            scope=scope,
            cache_path='spotify_cache/.cache',
        )
    )   
    return sp

sp_oauth = SpotifyOAuth(
            client_id=Keys.CLIENT_ID, 
            client_secret=Keys.CLIENT_SECRET, 
            redirect_uri=Keys.REDIRECT_URI,
            scope=scope,
            cache_path='spotify_cache/.cache',
        )