import os
from dotenv import load_dotenv

# if on development put environment variables in .env 
# else if on production configure configure through heroku
basedir = os.path.abspath(os.path.dirname(__file__))
if os.path.exists(os.path.join(basedir, '.env')):
    load_dotenv(os.path.join(basedir, '.env'))

class FlaskConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-wont-guess-this-haha'

class SpotifyConfig:
    CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
    REDIRECT_URI = os.environ.get('SPOTIFY_REDIRECT_URI')
