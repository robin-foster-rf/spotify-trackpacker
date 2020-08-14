import spotipy
from spotipy.oauth2 import SpotifyOAuth
from random import choice
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

#def generateRandomString(length):
#    """Generates a random string containing numbers and letters
#    Used for the `state` argument when authenticating with Spotify
#    """
#    possibles = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
#    text = ''.join(choice(possibles) for i in range(length)))
#    return text


if __name__=="__main__":
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=Keys.CLIENT_ID, 
            client_secret=Keys.CLIENT_SECRET, 
            redirect_uri='http://example.com',
            scope=scope,
            #cache_path='spotify_cache/.cache',
            username='r.foster',
        )
    )   

    #results = sp.current_user_saved_tracks()
    #for idx, item in enumerate(results['items'])

    if False:
        r = sp.user_playlist_create(
            user=sp.current_user()['id'], 
            name='knapsack-test', 
            public=True, 
            description='a knapsack test playlist'
        )