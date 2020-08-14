from flask import render_template, flash, redirect, request, session, url_for
from datetime import datetime
from spotipy import Spotify

from app import app
from app.forms import AuthenticateSpotifyForm, CreatePlaylistForm

from app.spotify import _sp_oauth, get_saved_tracks, create_playlist
from app.pack import solve, SolverException


@app.route('/')
@app.route('/index')
def index():
    tokens = session.get('tokens')
    if tokens:
        sp_oauth = _sp_oauth()
        if sp_oauth.is_token_expired(tokens):
            tokens = sp_oauth.refresh_access_token(tokens['refresh_token'])
            session['tokens'] = tokens
        sp = Spotify(auth=tokens['access_token'])
        user = sp.current_user()
        session['current_user'] = user
        playlist = session.get('last_created_playlist')
        return render_template('index.html', 
            user=user,
            playlist=playlist,
        ) 
    else:
        return render_template('index.html')


@app.route('/authorize')
def authorize():
    sp_oauth = _sp_oauth()
    tokens = session.get('tokens')
    if tokens:
        if sp_oauth.is_token_expired(tokens):
            tokens = sp_oauth.refresh_access_token(tokens['refresh_token'])
            session['tokens'] = tokens
        return redirect(url_for('callback', code=tokens['access_token']))
    else:
        auth_url = sp_oauth.get_authorize_url()
        return render_template('authorize.html', auth_url=auth_url)    


@app.route('/callback')
def callback():
    sp_oauth = _sp_oauth()
    url = request.url
    code = sp_oauth.parse_response_code(url)
    tokens = sp_oauth.get_access_token(code, as_dict=True, check_cache=False)
    session['tokens'] = tokens
    sp = Spotify(tokens['access_token'])
    user = sp.current_user()
    session['user'] = user
    return render_template('callback.html', user=user)


@app.route('/logout')
def logout():
    #session.pop('user', None)
    #session.pop('access_token', None)
    session.clear()
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

        for t in selected_tracks:
            flash(t)

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
