from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class AuthenticateSpotifyForm(FlaskForm):
    submit = SubmitField('Log in with Spotify')



from wtforms import IntegerField
from wtforms.validators import NumberRange
class CreatePlaylistForm(FlaskForm):
    duration = IntegerField(
        'Duration (seconds)', 
        validators=[DataRequired(), NumberRange(min=0)]
    )
    submit = SubmitField('Create playlist')
