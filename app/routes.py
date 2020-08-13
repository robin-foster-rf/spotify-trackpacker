from flask import render_template, flash, redirect, request, session, url_for
from datetime import datetime

from app import app
from app.forms import AuthenticateSpotifyForm, CreatePlaylistForm

@app.route('/')
@app.route('/index')
def index():
    access_token = session.get('access_token')
    if access_token:
        return redirect('/authorize')
    else:
        return render_template('index.html')


@app.route('/home')
def home():
    access_token = session.get('access_token')
    last_created = session.get('last_created_playlist')
    if access_token:
        return render_template('home.html', playlist=last_created)
    else:
        return redirect('index.html')


from spotipy import SpotifyOAuth, Spotify
from config import SpotifyConfig
from app.spotify import scope
from uuid import uuid4


sp_oauth = SpotifyOAuth(
    client_id=SpotifyConfig.CLIENT_ID, 
    client_secret=SpotifyConfig.CLIENT_SECRET, 
    redirect_uri=SpotifyConfig.REDIRECT_URI,
    scope=scope,
    username=uuid4()
)


@app.route('/authorize')
def authorize():
    access_token = ""

    token_info = sp_oauth.get_cached_token()

    if token_info:
        access_token = token_info['access_token']
    #else:
    #    url = request.url
    #    code = sp_oauth.parse_response_code(url)
    #    if code:
    #        token_info = sp_oauth.get_access_token(code)
    #        access_token = token_info['access_token']
    
    if access_token:
        return redirect('/callback'+'?'+access_token)
    else:
        auth_url = sp_oauth.get_authorize_url()
        return render_template('authorize.html', 
            auth_url=auth_url)


@app.route('/callback')
def callback():
    url = request.url
    code = sp_oauth.parse_response_code(url)
    if code:
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']

    session['access_token'] = access_token

    sp = Spotify(access_token)
    results = sp.current_user()
    session['user'] = results
    return render_template('callback.html', 
        results=results)


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('access_token', None)
    return redirect('/index')


from app.pack import solve

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    form = CreatePlaylistForm()
    if form.validate_on_submit():
        playlist_duration = request.form.get('duration', type=int)*1000
        tracks = get_saved_tracks()
        track_durations = [t[2] for t in tracks]
        selected, _ = solve(playlist_duration, track_durations)
        selected_tracks = [t for i, t in enumerate(tracks) if i in selected]
        
        flash(selected_tracks)

        playlist = create_playlist(
            [t[1] for t in selected_tracks], 
            'knapsack t={:d}s'.format(playlist_duration//1000), 
            'created at '+datetime.now().strftime("%Y-%b-%d %H:%M:%S"), 
        )
        session['last_created_playlist'] = playlist
        return redirect('/home')
    return render_template('generate.html', form=form)


def get_saved_tracks():
    sp = Spotify(session['access_token'])

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
    sp = Spotify(session['access_token'])

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
