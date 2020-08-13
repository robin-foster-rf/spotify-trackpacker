from flask import render_template, flash, redirect, request, session, url_for
from datetime import datetime

from app import app
from app.forms import AuthenticateSpotifyForm, CreatePlaylistForm

@app.route('/')
@app.route('/index')
def index():
    access_token = session.get('access_token')
    if access_token:
        last_created = session.get('last_created_playlist')
        return render_template('index.html', playlist=last_created)
    return render_template('index.html')


from uuid import uuid4
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

from config import SpotifyConfig
from app.spotify import scope
from app.pack import solve, SolverException

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


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    form = CreatePlaylistForm()
    if form.validate_on_submit():
        duration_h = request.form.get('duration_h', type=int) or 0
        duration_m = request.form.get('duration_m', type=int) or 0
        duration_s = request.form.get('duration_s', type=int) or 0
        playlist_duration_s = duration_h*3600 + duration_m*60 + duration_s
        playlist_duration_ms = playlist_duration_s*1000

        tracks = get_saved_tracks()
        track_durations_ms = [t[2] for t in tracks]

        try:
            selected, _ = solve(playlist_duration_ms, track_durations_ms)
        except SolverException:
            flash('No solution possible for that duration. Try something else')
            return render_template('generate.html', form=form)


        selected_tracks = [t for i, t in enumerate(tracks) if i in selected]
        selected_track_ids = [t[1] for t in selected_tracks]

        flash(selected_tracks)

        creation_time = datetime.now()
        duration_strings = [
            f'{duration_h:2d}h' if duration_h>0 else '',
            f'{duration_m:2d}m' if duration_m>0 else '', 
            f'{duration_s:2d}s' if duration_s>0 else '',
        ]
        name = 'trackpack '+' '.join(duration_strings)
        description = 'created at '+creation_time.strftime('%Y-%b-%d %H:%M:%S')

        playlist = create_playlist(
            selected_track_ids,
            name, 
            description,
        )
        session['last_created_playlist'] = playlist
        return redirect(url_for('index'))
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