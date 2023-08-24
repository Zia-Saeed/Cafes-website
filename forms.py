from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField, IntegerField, FloatField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, URL, Email, length


class Register(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired(), Email(), length(min=8, max=80)])
    password = PasswordField(label="Password", validators=[DataRequired(), length(min=8, max=30)])
    name = StringField(label="Name", validators=[DataRequired(), length(min=3)])
    submit = SubmitField(label="Sign Me up!")


class Login(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired(), Email(), length(max=80)])
    password = PasswordField(label="Password", validators=[DataRequired(), length(min=8)])
    submit = SubmitField(label="Login")


class Contact(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired(), Email(), length(max=80)])
    name = StringField(label="Name", validators=[DataRequired(), length(max=60)])
    message = TextAreaField(label="Message", validators=[DataRequired()])
    submit = SubmitField(label="Send")


class AddCafe(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired(), length(max=100)])
    map_url = StringField(label="Map Url", validators=[DataRequired(), URL()])
    img_url = StringField(label="Image Url", validators=[DataRequired(), URL()])
    location = StringField(label="Location", validators=[DataRequired()])
    seats = StringField(label="Number of Seats", validators=[DataRequired()])
    price = StringField(label="Coffee Price", validators=[DataRequired()])
    sockets = BooleanField('Sockets', default=True)
    toilet = BooleanField('Toilet', default=True)
    wifi = BooleanField('Wifi', default=True)
    can_take_calls = BooleanField('Can_take_calls', default=True)
    submit = SubmitField(label="ADD")


class Review(FlaskForm):
    body = CKEditorField("Review", validators=[DataRequired()])
    submit = SubmitField("Submit Review")
