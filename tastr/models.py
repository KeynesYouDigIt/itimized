"""This file creates models, 
which are passed to the router in views.py to take form data and store it.

configurations are in init.py and tasks for setup are in db_switch.py"""

from tastr import db
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

User_rec_ratings_join  = db.Table(
                                'User_rec_ratings_join',
                                db.Column(
                                        'user_id', db.Integer,
                                        db.ForeignKey('user.id')),
                                db.Column(
                                        'recipie_id', db.Integer,
                                           db.ForeignKey('recipe.id')),
                                db.Column('rating', db.SmallInteger))


Recipe_ingredients = db.Table(
                                'Recipe_ingredients',
                                db.Column(
                                        'rec_id', db.Integer,
                                        db.ForeignKey('recipe.id',
                                                      onupdate = "CASCADE",
                                                      ondelete = "CASCADE")),
                                db.Column(
                                        'ingredient_id', db.Integer,
                                        db.ForeignKey('ingredient.id',
                                                      onupdate="CASCADE",
                                                      ondelete="CASCADE")
                                        ))


class User(db.Model, UserMixin):
    """This model allows user storage.

    id is an auto incrementing primary key

    username is a username, must be provided and unique

    email is email, does not have to be unique

    password_hash is the encrypted storage of the user password
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=False)

    password_hash = db.Column(db.String)

    @property
    def serialize(self):
        return {
            'id'        : self.id,
            'username'  : self.username,
            'email'     : self.email
        }

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()



class Recipe(db.Model):
    """This model stores channels that orgs are distrubuting content through.

    id is an auto incrementing primary key

    name is the tag as a string
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False, unique=True, index=True)
    author = db.Column(
                        db.Integer,
                        db.ForeignKey('user.id',
                                      onupdate="CASCADE",
                                      ondelete="CASCADE"),
                        nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    nutrtion_facts = db.Column(db.Text, nullable=True)
    _ingredients = db.relationship('Ingredient',
                                    secondary = Recipe_ingredients,
                                    lazy = 'joined',
                                    backref = db.backref(
                                                        'recipes',
                                                        lazy='dynamic'))

    @property
    def serialize(self):
        return {
            'id'                : self.id,
            'name'              : self.name,
            'author'            : User.query.filter_by(id=self.author)
                                            .first().serialize,
            'instructions'      : self.instructions,
            'nutrition_facts'   : self.nutrtion_facts,
            'ingredients'       :self.ingredients
        }

    @property
    def ingredients(self):
        return ','.join([ t.name for t in self._ingredients ])

    @ingredients.setter
    def ingredients(self, string):
        if string:
            self._ingredients = [
                                Ingredient.get_or_create(name)
                                for name in string.split(',')
                                ]
        else:
            self._ingredients = []

    def uses(self, i):
        # takes an ingredient name and checks for it in the recipe
        return i in [ing.name for ing in self._ingredients]

    def get_author(self):
        return User.query.filter_by(id=self.author).first()

class Ingredient(db.Model):
    """
    stuff!
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    vegan = db.Column(db.Boolean, default=False)
    kosher = db.Column(db.Boolean, default=False)

    @property
    def serialize(self):
        return {
            'id'        : self.id,
            'name'      : self.name,
            'vegan'     : self.vegan,
            'kosher'    : self.kosher
        }

    @staticmethod
    def get_or_create(name):
        try:
            return Ingredient.query.filter_by(name=name).one()
        except:
            return Ingredient(name=name)