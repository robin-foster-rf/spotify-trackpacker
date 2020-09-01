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
    'ugc-image-upload', 
])

def _sp_oauth():
    """
    get spotipy oauth object
    """
    sp_oauth = SpotifyOAuth(
        client_id=SpotifyConfig.CLIENT_ID, 
        client_secret=SpotifyConfig.CLIENT_SECRET, 
        redirect_uri=SpotifyConfig.REDIRECT_URI,
        scope=scope,
    )
    return sp_oauth

def _sp_session():
    """
    get spotipy api object, refreshing tokens if needed
    """
    sp_oauth = _sp_oauth()
    if sp_oauth.is_token_expired(session['tokens']):
        tokens = sp_oauth.refresh_access_token(session['tokens']['refresh_token'])
        session['tokens'] = tokens
    sp = Spotify(session['tokens']['access_token'])
    return sp

def get_saved_tracks():
    sp = _sp_session()

    offset = 0
    limit = 50
    total = limit
    tracks = []
    while offset<total:
        r = sp.current_user_saved_tracks(limit=limit, offset=offset)
        tracks += [t['track'] for t in r['items']]
        if total==limit:
            total = r['total']
        offset += limit
        print(offset, total)
    return tracks


def get_tracks_from_seed_tracks(seed_track_ids):
    sp = _sp_session()
    limit = 100 # recomendations endpoint only gives 100 tracks max but seems to
    # give different results if called more than once or with an offset parameter 
    r = sp.recommendations(seed_tracks=seed_track_ids, limit=limit, country=session['user']['country'])
    tracks = r['tracks']
    # include original seeds in list of tracks returned (TODO: probs want to preferentially include the seed tracks in the generated playlist if possible)
    r = sp.tracks(seed_track_ids)
    tracks += r['tracks']
    return tracks


def get_tracks_from_seed_artist(seed_artist_ids):
    sp = _sp_session()
    limit = 100
    r = sp.recommendations(seed_artists=seed_artist_ids, limit=limit, country=session['user']['country'])
    tracks = r['tracks']
    return tracks


def get_tracks_from_genre(seed_genres):
    sp = _sp_session()
    limit = 100
    r = sp.recommendations(seed_genres=seed_genres, limit=limit, country=session['user']['country'])
    tracks = r['tracks']
    return tracks


def create_playlist(track_ids, name, description=''):
    sp = _sp_session()

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


def get_track_art_url(track, res=300):
    """
    get url for track artwork with given resolution

    params:
        track : track dict object as returned by spotify api
        res : image resolution in pixels - one of {640, 300, 64}
    returns:
        url : string
    """
    ims = track['album']['images']
    url = ''
    for im in ims:
        if im['height'] == res:
            url = im['url']
    return url


def get_genres():
    sp = _sp_session()
    r = sp.recommendation_genre_seeds()
    return r['genres']


class TrackStream:
    """
    Generator for tracks - yields as many tracks as you'll need to meet a target
    length
    """
    pass