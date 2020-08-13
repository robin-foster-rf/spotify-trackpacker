import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class FlaskConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-wont-guess-this-haha'

class SpotifyConfig:
    CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
    REDIRECT_URI = os.environ.get('SPOTIFY_REDIRECT_URI')
