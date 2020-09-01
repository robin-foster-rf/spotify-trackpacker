from flask import render_template, flash, redirect, request, session, url_for, jsonify
from datetime import datetime
from spotipy import Spotify

from app import app
from app.forms import (AuthenticateSpotifyForm, CreatePlaylistForm, 
    CreatePlaylistFromSeedForm)
from app.spotify import _sp_oauth, _sp_session
import app.spotify as spotify
from app.pack import solve, SolverException
from app.art import create_cover


@app.route('/')
@app.route('/index')
def index():
    tokens = session.get('tokens')
    if tokens:
        sp = _sp_session()
        user = sp.current_user()
        session['current_user'] = user
        playlist = session.get('last_created_playlist')
        playlist_tracks = session.get('last_created_playlist_tracknames')
        return render_template('index.html', 
            user=user,
            playlist=playlist,
            playlist_tracks=playlist_tracks,
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
    message = {
        'alert_type': 'alert-success', 
        'content': 'successfully logged in as '+user['display_name']
    }
    flash(message)
    return redirect(url_for('index'))


@app.route('/logout') 
def logout():
    session.clear()
    message = {
        'alert_type': 'alert-warning', 
        'content': 'logged out',
    }
    flash(message)
    return redirect('/index')


@app.route('/generate_simple', methods=['GET', 'POST'])
def generate_simple():
    form = CreatePlaylistForm()
    if form.validate_on_submit():
        duration_h = request.form.get('duration_h', type=int) or 0
        duration_m = request.form.get('duration_m', type=int) or 0
        duration_s = request.form.get('duration_s', type=int) or 0
        playlist_duration_s = duration_h*3600 + duration_m*60 + duration_s
        playlist_duration_ms = playlist_duration_s*1000

        tracks = spotify.get_saved_tracks()
        track_names = [t['name'] for t in tracks]
        track_durations_ms = [t['duration_ms'] for t in tracks]

        try:
            selected, _ = solve(playlist_duration_ms, track_durations_ms)
        except SolverException:
            flash('No solution possible for that duration. Try something else')
            return render_template('generate.html', form=form)

        selected_tracks = [t for i, t in enumerate(tracks) if i in selected]
        selected_track_ids = [t['id'] for t in selected_tracks]

        creation_time = datetime.now()
        duration_strings = [
            f'{duration_h:2d}h' if duration_h>0 else '',
            f'{duration_m:2d}m' if duration_m>0 else '', 
            f'{duration_s:2d}s' if duration_s>0 else '',
        ]
        name = 'trackpack '+' '.join(duration_strings).strip()
        description = 'created at '+creation_time.strftime('%Y-%b-%d %H:%M:%S')

        playlist = spotify.create_playlist(
            selected_track_ids,
            name, 
            description,
        )
        session['last_created_playlist'] = playlist
        session['last_created_playlist_tracknames'] = [track_names[i] for i in selected]

        # create cover art from top 5 tracks in playlist
        sp = Spotify(session['tokens']['access_token'])
        cover_urls = [spotify.get_track_art_url(t) for t in selected_tracks[:5]]
        img_b64 = create_cover(cover_urls)
        sp.playlist_upload_cover_image(playlist['id'], img_b64)

        return redirect(url_for('index'))
    return render_template('generate.html', form=form)


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    form = CreatePlaylistFromSeedForm()
    genres = spotify.get_genres()
    form.genre.choices = list(zip(genres, genres))
    seed_type = list(form.seed_type)

    if form.validate_on_submit():
        duration_h = request.form.get('duration_h', type=int) or 0
        duration_m = request.form.get('duration_m', type=int) or 0
        duration_s = request.form.get('duration_s', type=int) or 0
        playlist_duration_s = duration_h*3600 + duration_m*60 + duration_s
        playlist_duration_ms = playlist_duration_s*1000

        seed_type = form.seed_type.data
        if seed_type=='user_library':
            tracks = spotify.get_saved_tracks()
        elif seed_type=='genre':
            tracks = spotify.get_tracks_from_genre(form.genre.data)
        elif seed_type=='seed_artist':
            tracks = spotify.get_tracks_from_seed_artist(form.seed_artist.data)
        elif seed_type=='seed_tracks':
            tracks = spotify.get_tracks_from_seed_tracks(form.seed_tracks.data)
        
        track_names = [t['name'] for t in tracks]
        track_durations_ms = [t['duration_ms'] for t in tracks]

        try:
            selected, _ = solve(playlist_duration_ms, track_durations_ms)
        except SolverException:
            message = {
                'alert_type': 'alert-warning', 
                'content': 'No solution possible for that duration. Try something else',
            }
            flash(message)
            return render_template('generate_from_seed.html', form=form)

        selected_tracks = [t for i, t in enumerate(tracks) if i in selected]
        selected_track_ids = [t['id'] for t in selected_tracks]

        creation_time = datetime.now()
        duration_strings = [
            f'{duration_h:2d}h' if duration_h>0 else '',
            f'{duration_m:2d}m' if duration_m>0 else '', 
            f'{duration_s:2d}s' if duration_s>0 else '',
        ]
        name = 'trackpack '+' '.join(duration_strings).strip()
        description = 'created at '+creation_time.strftime('%Y-%b-%d %H:%M:%S')

        playlist = spotify.create_playlist(
            selected_track_ids,
            name, 
            description,
        )
        session['last_created_playlist'] = playlist
        session['last_created_playlist_tracknames'] = [track_names[i] for i in selected]

        # create cover art from top 5 tracks in playlist
        sp = _sp_session()
        cover_urls = [spotify.get_track_art_url(t) for t in selected_tracks[:5]]
        img_b64 = create_cover(cover_urls)
        sp.playlist_upload_cover_image(playlist['id'], img_b64)

        message = {
            'alert_type': 'alert-success',
            'content': 'new playlist created'
        }
        flash(message)

        return redirect(url_for('index'))
    return render_template('generate_from_seed.html', form=form, seed_type=seed_type)


# wrapper for spotify search - used to populate search boxes on the fly from user inputs
@app.route('/search', methods=['GET', 'POST'])
def search():
    sp = Spotify(session['tokens']['access_token'])
    q = request.args.get('q')
    search_type = request.args.get('type')
    r = sp.search(q, limit=15, type=search_type)
    return jsonify(r)


@app.route('/search_page', methods=['GET', 'POST'])
def search_page():
    return render_template('search_page.html')

