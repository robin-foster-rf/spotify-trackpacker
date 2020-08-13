from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

from config import SpotifyConfig

# scope = ' '.join([
#     'user-read-playback-state', 
#     'user-modify-playback-state', 
#     'user-read-currently-playing', 
#     'streaming', 
#     'app-remote-control', 
#     'user-read-email', 
#     'user-read-private', 
#     'playlist-read-collaborative', 
#     'playlist-modify-public', 
#     'playlist-read-private', 
#     'playlist-modify-private', 
#     'user-library-modify', 
#     'user-library-read', 
#     'user-top-read', 
#     'user-read-playback-position', 
#     'user-read-recently-played',
# ])

scope = ' '.join([
    'user-read-private', 
    'user-read-email', 
    'user-library-read', 
    'user-library-modify', 
    'user-top-read', 
    'playlist-read-collaborative', 
    'playlist-modify-public', 
    'playlist-read-private', 
    'playlist-modify-private', 
])

def init_spotify():
    sp = Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SpotifyConfig.CLIENT_ID, 
            client_secret=SpotifyConfig.CLIENT_SECRET, 
            redirect_uri=SpotifyConfig.REDIRECT_URI,
            scope=scope,
            cache_path='spotify_cache/.cache',
        )
    )   
    return sp


sp_oauth = SpotifyOAuth(
            client_id=SpotifyConfig.CLIENT_ID, 
            client_secret=SpotifyConfig.CLIENT_SECRET, 
            redirect_uri=SpotifyConfig.REDIRECT_URI,
            scope=scope,
            cache_path='spotify_cache/.cache',
        )
