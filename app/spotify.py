from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from flask import session

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

def _sp_oauth():
    sp_oauth = SpotifyOAuth(
        client_id=SpotifyConfig.CLIENT_ID, 
        client_secret=SpotifyConfig.CLIENT_SECRET, 
        redirect_uri=SpotifyConfig.REDIRECT_URI,
        scope=scope,
    )
    return sp_oauth

def get_saved_tracks():
    sp = Spotify(session['tokens']['access_token'])

    offset = 0
    limit = 50
    total = limit
    tracks = []
    while offset<total:
        r = sp.current_user_saved_tracks(limit=limit, offset=offset)
        tracks += [
            (t['track']['name'], t['track']['id'], t['track']['duration_ms']) 
                for t in r['items'] 
        ]
        if total==limit:
            total = r['total']
        offset += limit
        print(offset, total)
    return tracks


def create_playlist(track_ids, name, description=''):
    sp = Spotify(session['tokens']['access_token'])

    r = sp.user_playlist_create(
        session['user']['id'], 
        name=name, 
        public=True,
        description=description
    )
    playlist = r

    r = sp.user_playlist_add_tracks(
        session['user']['id'], 
        playlist_id=r['id'], 
        tracks=track_ids,
    )
    return playlist