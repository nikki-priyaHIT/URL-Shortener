from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import URL, DataRequired

class InputForm(FlaskForm):
    url = StringField("URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Shorten")