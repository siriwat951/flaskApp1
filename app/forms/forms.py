from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField,
                     RadioField, EmailField, PasswordField)
from wtforms.validators import InputRequired, Length, Regexp, EqualTo, Email

class CourseForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(),
                                             Length(min=10, max=100)])
    description = TextAreaField('Course Description',
                                validators=[InputRequired(),
                                            Length(max=200)])
    price = IntegerField('Price', validators=[InputRequired()])
    level = RadioField('Level',
                       choices=['Beginner', 'Intermediate', 'Advanced'],
                       validators=[InputRequired()])
    available = BooleanField('Available', default='checked')

from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField,
                     RadioField)
from wtforms.validators import InputRequired, Length


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(),
                                             Length(min=10, max=100)])
    email = EmailField('Email',validators=[InputRequired(),
                                            Email(message="Invalid Email")])
    password = PasswordField('Password', validators=[InputRequired(),
                                            Regexp(r'^(?=.*\d)', message="Password must contain at least one number")])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(),
                                            EqualTo('password', message="Passwords must match")])
    