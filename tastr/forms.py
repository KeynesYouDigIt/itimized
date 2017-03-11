"""This file creates classes, 
which are passed to the router in views.py as displayable objects passed 
to Jinja for rendering."""

from flask_wtf import Form
from wtforms.fields import StringField, PasswordField, \
BooleanField, SubmitField, TextAreaField
from wtforms.validators import *
from wtforms import ValidationError
from .models import *
from wtforms.fields.html5 import URLField

class SignupForm(Form):
    """typical user registration form.
    username must be 2-90 characters in length with no specials, unique.

    password only has to match confirm password.

    email is strictly optional, can be used for multiple accounts. 
    This is because the site proritizes flexibility and anonymnity over 
    saftey or user workflow control """

    username = StringField('username&nbsp',
                    validators=[
                        DataRequired(), 
                        Length(2,80, \
                            message='thats too long or to short. keep it within 2 to 80 chars.'+\
                            '\n Dont really know why you want to type that much anyway....'),
                        Regexp('^[A-Za-z0-9_]{2,}',
                        message='stop it with the weird username!'+\
                        'must be letters, numbers, and _')
                    ])
    password = PasswordField('password',
                    validators=[
                    DataRequired(),
                    EqualTo('password_confirm',
                        message='slow down there partner, which is it?\n '+\
                        'you put something different in \'password\' and'+\
                        ' \'confirm password\'...')
                    ])
    password_confirm = PasswordField('confirm password&nbsp',
                    validators=[DataRequired()
                    ])
    Email = StringField('Email <font size="1">(optional)</font> &nbsp  &nbsp', 
                    validators = [
                    Optional(),
                    Length(1,120),
                    Email(message='valid email please.')])

    def validate_username(self, username_field):
        if User.query.filter_by(username=username_field.data).first():
            raise ValidationError('somebody beat you to that username.'
                                    'Common, be original!')


class LoginForm(Form):
    """typical login  form.
    remember_me boolean sends a cookie to keep the login session for 
    500 days or until cookies are cleared. """

    username = StringField('Username &nbsp', 
        [InputRequired(message='I need this bit!')])

    password = PasswordField('Password &nbsp', 
        [InputRequired(message='I need this bit!')])

    remember_me = BooleanField('<font size="1">gimmie a cookie to '
                               'keep me logged in</font> &nbsp  &nbsp',
                                default = True)

    submit = SubmitField('Log In')


class DataForm(Form):
    """This form allows for both creation and editing of recipes.
    url will be like the name of the recipe with a '/' added for easy routing
    and a web aesthetic when displayed.

    content is an open text field containing the content of the recipe
    with no restrictions (wtforms escapes html).

    ingredients are the main workflow step for viewing other user's recipes,
    no special characters allowed. They are comma seperated when entered.

    The last few lines in validation 
    prevent separate records for the same ingredients.
    """
    name = StringField('enter the name here for the recipe   _> &nbsp',
                        validators = [
                            InputRequired(
                                            message='I need this bit!'),
                            Regexp('^[A-Za-z0-9_]{2,}',
                                   message='ingredients must be'
                                           ' letters and numbers only')])

    instructions = TextAreaField('Tell us how to make it here _>')

    ingredients = StringField('add ingredients! <br><br>'
        'select from the list or seperate each one with a comma<br><br>'
        '<em> <font size="2">'
        'pick from the list of existing ingredients'
        '</font></em>&nbsp  &nbsp',
        validators = [
            Length(2, 25000000,
                   message='thats too long. keep it within 25m chars.'),
            Optional(),
            Regexp('^[A-Za-z_]{2,}',
                    message='ingredients must be letters, and _s')])

    def validate_unique_name(self, name_field):
        if Recipe.query.filter_by(username=name_field.data).first():
            raise ValidationError('somebody beat you to that recipe name.'
                                    'Common, be original!')


    def validate(self):
        #this overwrites the validate method of the form class
        if not Form.validate(self):
            return False
            
        stripped = [t.strip() for t in self.ingredients.data.split(',')]
        legit = [t for t in stripped if t]
        as_set = set(legit)
        self.ingredients.data = ','.join(as_set)


        return True


class Ingredient_search_form(Form):
    """same as data form just recipes
    """
    ingredients = StringField('<br><br>'
                              '<em> <font size="2">'
                              'pick existing ingredients'
                              '</font></em>'
                              '<tr>  </tr>',
                              validators=[
                                  Length(2, 25,
                                         message='thats too long. keep it within 25 chars.'),
                                  Optional(),
                                  Regexp('^[A-Za-z_]{2,}',
                                         message='ingredients must be letters, and _s')])