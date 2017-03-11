"""This file creates routes and handles all logic based on user input.

It uses variables generated by forms.py and models.py and renders them to
Jinja2 templates stored in the templates folder."""


from flask import render_template, url_for,\
                    request, redirect, flash,\
                    abort, jsonify, session
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy.sql import text
from tastr import *
from models import *
from forms import *

# social auth tools
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

#client id and appname for google social sign in
CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "tastr"


@app.route('/login', methods=['GET','POST'])
def login():
    # standard login page.
    form = LoginForm()
    session['state'] = ''.join(random.choice(string.ascii_uppercase\
                                             + string.digits)
                               for x in xrange(32))
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash (' welcome {}, you can now edit recipes.'.format(user.username))
            return redirect(request.args.get('next') or url_for('starter'))
        else:
            # vague error does not let the user know if username attempted exists.
            flash('!!: nope, pwd or username is wrong.')

    return render_template(
                            'login.html',
                            form=form,
                            state=session['state'])


@app.route('/gconnect',  methods=['POST'])
def gconnect():
    '''This goes through a large span of checks to use Oauth with Google.
    It is not a template rendering route, just the route used to validate
    social sign on.'''

    # The first check is the State token, with no valid state nothing else
    # should be checked.
    print (request.args.get('state'))
    print(session)
    if request.args.get('state') != session['state']:
        state_bad_response = make_response(json.dumps('request state is not '
                                                       'session state.'))
        state_bad_response.headers['Content-Type'] = 'application/json'
        return state_bad_response
    print('state is good, get auth code')
    print(request)
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # use method on cred object to send original google button to google
        # try to obtain final credentials
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
                json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('creds from google')
    print(credentials)

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        print('error in request for final google token')
        print(result.get('error'))
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('no error in result')
    print(result)

    # What google gave me in the first request for the users account needs to
    # match the user id provided in the result from the token server
    if result['user_id'] != credentials.id_token['sub']:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('user in token request matches user in ouath creds request')

    # The application ID should also match
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # We now believe the user is valid, are they already logged in?
    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    #session.clear() is called at the logout URL to clear these
    if stored_access_token is not None and \
                    credentials.id_token['sub'] == stored_gplus_id:
        print('Current user is already connected')
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('user is now logging in!!!')

    # Store the access token in the session
    session['access_token'] = credentials.access_token
    session['gplus_id'] = credentials.id_token['sub']

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    data = requests.get(userinfo_url, params=params).json()

    # the username field needs to be unique, so gplus_id and name are concated
    # for storage in a few lines
    session['username'] = data['name'] + '  [' + data['email'] + ']'
    print('sess goog user')
    print session['username']

    user = User.query.filter_by(username=session['username']).first()
    if user:
        print('found user, welcoming them back')
        login_user(user, True)
        flash(' welcome {}, you can now edit recipes.'.format(user.username))
        return redirect(request.args.get('next') or url_for('starter'))

    print('user appears to be ...')
    print(user)
    goog_noob = User(email=data['email'],
                username=session['username'],
                password=session['state'])

    # pwd will just be the tastr state token from first logon.
    # spoofing a password satisfies the db requirements and is still as hard
    # to spoof as the original state token.
    db.session.add(goog_noob)
    db.session.commit()
    user = User.query.filter_by(username=session['username']).first()
    if user:
        print('user stored and retrieved!')
        login_user(user, True)
        flash(' welcome {}, you can now edit recipes.'.format(user.username))
        return redirect(request.args.get('next') or url_for('starter'))

    response = make_response(
            json.dumps("gconnect function did not store/get user"), 500)
    print "gconnect function did not store/get user"
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/logout')
def logout():
    # standard logout page
    flash (' thanks for hanging out! you are now in anon mode (view only).')
    logout_user()
    session.clear()
    return redirect(request.args.get('next') or url_for('login'))


@app.route('/sign_up', methods=['GET','POST'])
def sign_up():
    # standard sign up form
    form=SignupForm()
    if form.validate_on_submit():
        email=form.Email.data
        username=form.username.data
        # Form data us used to create an instance of User
        noob = User(email=form.Email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(noob)
        db.session.commit()
        flash('Hello  %s, and welcome to Tastr!' % username)
        login_user(noob)
        return redirect('/start', code=302)

    return render_template(
                            'register.html',
                            form=form,
                            hfour='Sign up and start creating recipes!')


@app.route('/register')
@app.route('/')
def to_start ():
    # this is essentially a home page, taking a user to the start page if they
    # have logged in and to the sign up page if they have not.
    if current_user.is_authenticated:
        return redirect('/start', code=302)
    else:
        return redirect('/sign_up', code=302)


@app.route('/start', methods=['GET','POST'])
@login_required
def starter():
    # The starter page shows a logged in user their posts, 
    # and renders a single field to start a recipe by entering the recipe name.
    add_form=DataForm()
    if add_form.validate_on_submit():
        # when the post name is entered, forward the user on to write the 
        # other peices of the age
        return redirect(url_for('add', recipe=add_form.name.data))
    else:
        print 'no form validation'

    query_user = """select * from Recipe where author = :usr"""
    return render_template(
                            'user.html',
                            form=add_form,
                            active_user=current_user,
                            recipes=db.engine.execute(text(query_user),
                                  {'usr': current_user.id}).fetchall())


@app.route('/edit/<recipe>', methods=['GET', 'POST'])
@login_required
def add(recipe):
    # This page allows for both the adding and editing of recipe.
    # In this app, recipe name is unique, so author is checked only after
    # recipe is found.
    edit_recipe = Recipe.query.filter_by(name=recipe).first()
    print 'edit recipe'
    print edit_recipe
    if edit_recipe:
        print 'CHECK'
        print current_user.id
        print edit_recipe.author
        if current_user.id != edit_recipe.author:
            abort(401)
        print 'edit recipe!!!!!!!!!!'
        # the recipe already exists in the database, lets render for editing.
        recipe_edit_form = DataForm(obj=edit_recipe)
        print dir(recipe_edit_form)
        if recipe_edit_form.validate_on_submit():
            print "recipe_edit validated"
            recipe_edit_form.populate_obj(edit_recipe)
            db.session.commit()
            flash(" the recipe '{}' has been edited"
                  .format(recipe_edit_form.name.data))
            return redirect(url_for('render_user_recipe',
                                    user_id=edit_recipe.author,
                                    recipe_name=recipe_edit_form.name.data))
        return render_template (
                                'add.html',
                                form=recipe_edit_form,
                                name=edit_recipe.name,
                                existing_recipe=edit_recipe)
    else:
        # the recipe does not exists in the database, is rendered for creation.
        start_recipe = Recipe(name=recipe)
        recipe_add_form = DataForm(obj=start_recipe)
        if recipe_add_form.validate_on_submit():
            new_recipe = Recipe(
                                name=recipe_add_form.name.data,
                                instructions=recipe_add_form.instructions.data,
                                ingredients=recipe_add_form.ingredients.data,
                                author=current_user.id)
            db.session.add(new_recipe)
            db.session.commit()
            print new_recipe
            print db.session
            flash(" the recipe '{}' has been created!"
                  .format(recipe_add_form.name.data))
            return redirect(url_for('render_user_recipe',
                                    user_id=new_recipe.author,
                                    recipe_name=new_recipe.name))
        return render_template(
                                'add.html',
                                form=recipe_add_form,
                                name=start_recipe.name)


@app.route('/<user_id>/<recipe_name>')
def render_user_recipe(user_id, recipe_name):
    #  retrieve and show the recipe
    author = User.query.filter_by(id=user_id).first()
    recipe = Recipe.query.filter_by(
                                    name=recipe_name,
                                    author=author.id).first_or_404()
    print 'recipe author'
    print author
    print 'recipe get'
    print recipe
    if recipe:
        return render_template(
                                'user_recipe.html',
                                recipe=recipe,
                                active_user=current_user)


@app.route('/by_ingredients/', methods=['GET', 'POST'])
@app.route('/by_ingredients/<ingredients>', methods=['GET', 'POST'])
def catch_ingredient(ingredients=None):
    select_form = Ingredient_search_form(ingredients=ingredients)
    if not ingredients:
        recipes_to_send = ['_none_']
        is_empty = True
    else:
        is_empty = False
        ingredients = ingredients.split(',')
        # gets recipes containing at least one ingredient
        recipes_to_send = Recipe.query.join(
                                    Ingredient.recipes
                                    ).filter(
                                            Ingredient.name.in_(ingredients)
                                            ).all()
        # the below solution is remarkably un elegant and will be fixed
        # in the future.
        check_again = True
        while check_again and len(recipes_to_send) > 0:
            check_again = False
            # we aren't done checking until all recipes pass OR
            # there are no more recipes
            for rec in recipes_to_send:
                print 'now checking'
                print rec.name
                for i in ingredients:
                    if not rec.uses(i):
                        print i
                        print 'is not used in '
                        print rec.name
                        recipes_to_send.remove(rec)
                        check_again = True
                        break
        print 'done checking, all recipes pass'

    if select_form.validate_on_submit():
        return redirect(url_for(
                                'catch_ingredient',
                                ingredients=select_form.ingredients.data))

    return render_template(
                            'by_ingredient.html',
                            empty=is_empty,
                            recipe_list=recipes_to_send,
                            form=select_form)

@app.route('/like/<user>/<recipe_name>')
@login_required
def like(user, recipe_name):
    # nothing is rendered here, this is simply the route for liking a page.
    # once successful, the original page is re - rendered.
    author = User.query.filter_by(username = user).first()
    like_post = Post.query.filter_by(name = recipe_name, user = author).first_or_404()
    like_post._liked.append(current_user)
    # as noted in the models, liked is a list of user objects, 
    # which is why append is used. the original attribute does not need to be 
    # overwritten.
    db.session.commit()
    flash(" liked  '{}'".format(post_name))
    return redirect(url_for('render_user_post', 
                            user=user,
                            post_name=post_name))

@app.route('/delete/<int:recipe_id>', methods=['GET','POST'])
@login_required
def kill_recipe(recipe_id):
    # page confirming the deletion of a post.
    # this can be accessed from the edit page.
    target_post = Recipe.query.get_or_404(recipe_id)
    if current_user != target_post.get_author():
        abort(401)
    if request.method == "POST":
        db.session.delete(target_post)
        db.session.commit()
        flash(" '{}' is gone.".format(target_post.name))
        return redirect(url_for('starter'))
    else:
        flash('!! this will delete post')
    return render_template('confirm_kill.html')


# REST API lives here


@app.route('/recipes/<int:recipe_id>')
def respond_recipe(recipe_id):
    get_rec = Recipe.query.filter_by(id=recipe_id).first()
    if get_rec:
        get_rec = get_rec.serialize
    else:
        get_rec = 'nothing found'
    return jsonify(get_rec)


@app.route('/ingredients/<int:ingredient_id>')
def respond_ing(ingredient_id):
    get_ing = Ingredient.query.filter_by(id=ingredient_id).first()
    if get_ing:
        get_ing = get_ing.serialize
    else:
        get_ing = 'nothing found'
    return jsonify(get_ing)


@app.route('/recipes/author/<username>')
def get_author_rec(username):
    user_id = User.get_by_username(username).id
    authors_recipes = Recipe.query.filter_by(author=user_id)
    all_rec = [rec.serialize for rec in authors_recipes]

    return jsonify(all_rec)

@app.route('/recipes/all')
def get_all_rec():
    all_rec = [rec.serialize for rec in Recipe.query.all()]

    return jsonify(all_rec)


@app.route('/ingredients/all')
def get_all_ing():
    all_ing = [ing.serialize for ing in Ingredient.query.all()]
    return jsonify(all_ing)


# docs page here for API

@app.route('/API')
def explain_api():
    return render_template('API_doc.html')


# error handlers are standard


@app.errorhandler(404)
def post_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(401)
def unauth(e):
    return render_template('401.html'), 401


@app.errorhandler(500)
def unauth(e):
    return render_template('500.html', error = e), 500


@app.context_processor
def inject_tags():
    # this final function is used to allow tags to be accessed by JavaScript.
    get_them_all = Ingredient.query.all()
    print get_them_all
    return dict(all_tags = Ingredient.query.all)