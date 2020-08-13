from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.html5 import IntegerField, IntegerRangeField
from wtforms.widgets.html5 import NumberInput
from wtforms.validators import DataRequired, NumberRange


class AuthenticateSpotifyForm(FlaskForm):
    submit = SubmitField('Log in with Spotify')



#class CreatePlaylistForm(FlaskForm):
#    duration = IntegerField(
#        'Duration (seconds)', 
#        validators=[DataRequired(), NumberRange(min=0)]
#    )
#    submit = SubmitField('Create playlist')

class CreatePlaylistForm(FlaskForm):
    duration_h = IntegerField(
        'hours', 
        default=0,
        widget=NumberInput(min=0, step=1),
    )
    duration_m = IntegerRangeField(
        'minutes', 
        default=4, 
        widget=NumberInput(min=0, max=59, step=1),
    )
    duration_s = IntegerRangeField(
        'seconds', 
        default=33, 
        widget=NumberInput(min=0, max=59, step=1),
    )
    submit = SubmitField('Create playlist')