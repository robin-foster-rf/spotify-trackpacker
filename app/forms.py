from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SubmitField, 
    SelectMultipleField, RadioField)
from wtforms.fields.html5 import IntegerField, IntegerRangeField
from wtforms.widgets.html5 import NumberInput
from wtforms.validators import DataRequired, NumberRange

class AuthenticateSpotifyForm(FlaskForm):
    submit = SubmitField('Log in with Spotify')


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


# bug in wtforms.SelectMultipleField validate_choice parameter
# see https://github.com/wtforms/wtforms/issues/606
# and solution PR here https://github.com/wtforms/wtforms/pull/607/files
# override since PR not yet in production version
class MySelectMultipleField(SelectMultipleField):
    def pre_validate(self, form):
        return True


class CreatePlaylistFromSeedForm(FlaskForm):
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
    seed_type = RadioField(
        'Generate from',
        choices=[
            ('user_library', 'Fetch from your saved library'),
            ('genre', 'Choose genre'),
            ('seed_artist', 'Choose seed artist'),
            ('seed_tracks', 'Choose seed tracks'),
        ], 
        default='user_library',
    )
    genre = MySelectMultipleField(
        'Genre',
        choices=[], # choices will be fetched from spotify api
        id='genre',
        render_kw={'class': 'form-control-genre'},
    )
    seed_artist = MySelectMultipleField(
        'Seed artist', 
        choices=[], # choices will be populated via javascript from user search
        id='seed-artist',
        render_kw={'class': 'form-control-seed-genre', 'multiple': 'multiple'},
    )
    seed_tracks = MySelectMultipleField(
        'Seed tracks',
        #validate_choice=False, # bug in wtforms - see above
        choices=[], # choices will be populated via javascript from user search
        id='seed-tracks',
    )
    submit = SubmitField('Create playlist')
    
    def validate(self):
        # first do individual field validation as defined in constructors above
        res = super(CreatePlaylistFromSeedForm, self).validate() 
        # now check that if one of the final three radio options is selected 
        # that the associated option box also has something selected
        seed_type = self.seed_type.data
        if seed_type=='genre':
            if len(self.genre.data)<1:
                msg = 'Choose at least one genre'
                self.genre.errors.append(msg)
                res = False
        elif seed_type=='seed_artist':
            if len(self.seed_artist.data)<1:
                msg = 'Choose at least one artist'
                self.seed_artist.errors.append(msg)
                res = False
        elif seed_type=='seed_tracks':
            if len(self.seed_tracks.data)<1:
                msg = 'Choose at least one track'
                self.seed_tracks.errors.append(msg)
                res = False
        return res