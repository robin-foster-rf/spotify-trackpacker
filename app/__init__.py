from flask import Flask
from flask_bootstrap import Bootstrap

from config import FlaskConfig

app = Flask(__name__)
bootstrap = Bootstrap(app) # for some reason bootstrap needs to be done before other app config...
app.config.from_object(FlaskConfig)

from app import routes