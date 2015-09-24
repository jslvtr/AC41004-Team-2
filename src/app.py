import base64
from functools import wraps
from werkzeug.exceptions import abort
from src.common.database import Database
from src.models.article import Article, NoSuchArticleExistException
from src.models.event import Event, NoSuchEventExistException
from src.models.eventregister import EventRegister
from src.models.image import Image

from src.models.permissions import Permissions
from src.models.user import User
from flask import Flask, session, jsonify, request, render_template, redirect, url_for, make_response
from src.common.sessions import MongoSessionInterface
import os
import uuid
from datetime import datetime

__author__ = 'jslvtr and stamas01'

mongodb_user = os.environ.get("MONGODB_USER")
mongodb_password = os.environ.get("MONGODB_PASSWORD")
mongo_url = os.environ.get("MONGODB_URL")
mongo_port = os.environ.get("MONGODB_PORT")
mongo_database = os.environ.get("MONGODB_DATABASE")

assert mongodb_user is not None, "The MongoDB user was not set. Create an environment variable MONGODB_USER"
assert mongodb_password is not None, "The MongoDB password was not set. Create an environment variable MONGODB_PASSWORD"
assert mongo_url is not None, "The MongoDB url was not set. Create an environment variable MONGODB_URL"
assert mongo_port is not None, "The MongoDB port was not set. Create an environment variable MONGODB_PORT"
assert mongo_database is not None, "The MongoDB database was not set. Create an environment variable MONGODB_DATABASE"

app = Flask(__name__)
app.session_interface = MongoSessionInterface(host=mongo_url,
                                              port=int(mongo_port),
                                              db=mongo_database,
                                              user=mongodb_user,
                                              password=mongodb_password)
assert app.session_interface is not None, "The app session interface was None even though we tried to set it!"

app.secret_key = os.urandom(32)
assert app.secret_key is not None, "The app secret key was None even though we tried to set it!"


def get_db():
    Database.initialize(mongodb_user, mongodb_password, mongo_url, int(mongo_port), mongo_database)


@app.errorhandler(404)
def not_found(ex):
    return render_template('404.html'), 404


@app.errorhandler(401)
def not_found(ex):
    return render_template('401.html'), 401


@app.errorhandler(500)
def not_found(ex):
    return render_template('500.html'), 500


@app.route('/')
def index():
    news = [article for article in Database.find("articles", {})]
    events = [event for event in Database.find("events", {})]

    return render_template('home.html',
                           events=events,
                           news=news)


@app.before_first_request
def init_db():
    Database.initialize(mongodb_user, mongodb_password, mongo_url, int(mongo_port), mongo_database)


@app.after_request
def layout(response):
    if response.content_type == 'text/html; charset=utf-8':
        data = response.get_data()
        data = data.decode('utf-8')
        if str(request.url_rule).startswith("/admin"):
            data = render_template('admin.html', access_level=get_access_level(), data=data, user=session['email'] if session.contains('email') and session['email'] is not None else None)
            data = render_template('layout.html', data=data, user=session['email'] if session.contains('email') and session['email'] is not None else None)
        else:
            data = render_template('layout.html', data=data, user=session['email'] if session.contains('email') and session['email'] is not None else None)
        response.set_data(data)

        return response
    return response


def secure(type):
    def tags_decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            if session.contains('email') and session['email'] is not None and User.find_by_email(
                    session['email']).allowed(type):
                return make_response(func(*args, **kwargs))
            else:
                abort(401)

        return func_wrapper

    return tags_decorator


def get_access_level():
    if session.contains('email') and session['email'] is not None:
        return User.find_by_email(session['email']).permissions
    return ""


@app.route('/admin', methods=['GET'])
@app.route('/admin/events', methods=['GET'])
@secure("events")
def events_get_admin():
    events = [event for event in Database.find("events", {})]
    return render_template('events_admin.html', events=events)


@app.route('/admin/upload', methods=['POST'])
@secure("events")
def upload_image():
    file_data = request.files['file']
    image = Image(file_data.read(),file_data.mimetype)
    image.save_to_db()
    return jsonify({"id": image.get_id()}), 200


@app.route('/images/<uuid:image_id>', methods=['GET'])
def images(image_id):
    image = Image.get_by_id(image_id)
    fr = make_response( image.get_data() )
    fr.headers['Content-Type'] = image.get_content_type()
    return fr


@app.route('/admin/permissions', methods=['GET'])
@secure("admin")
def permissions_get_admin():
    permissions = [permission_level for permission_level in Database.find(Permissions.COLLECTION, {})]
    return render_template('permissions_admin.html', permissions=permissions)


@app.route('/admin/permissions/<string:name>/<string:access>', methods=['GET'])
@secure("admin")
def change_permission(name, access):
    permission = Permissions.find_by_name(name)
    if access in permission.access:
        permission.access.remove(access)
    else:
        permission.access.append(access)
    permission.save_to_db()
    return jsonify({"message": "ok"}), 200


@app.route('/admin/permissions/<string:name>', methods=['DELETE'])
@secure("admin")
def remove_permission(name):
    Permissions.find_by_name(name).remove_from_db()
    return jsonify({"message": "ok"}), 200


@app.route('/admin/permissions', methods=['POST'])
@secure("admin")
def add_permission():
    json = request.get_json()
    name = json['name']
    access = json['access']

    permission = Permissions(name, access)
    permission.save_to_db()

    return jsonify({"message": "ok"}), 201


@app.route('/admin/events/add/<uuid:event_id>', methods=['GET'])
@secure("events")
def event_add_get(event_id):
    try:
        event = Event.get_by_id(event_id)
        return render_template('event_add.html', event=event.to_json())
    except NoSuchEventExistException:
        abort(404)


@app.route('/admin/event', methods=['POST'])
@secure("events")
def event_add_post():
    try:
        start = datetime.strptime(request.form.get('start'), '%m/%d/%Y %I:%M %p')
        end = datetime.strptime(request.form.get('end'), '%m/%d/%Y %I:%M %p')
        new_event = Event(request.form.get('title'), request.form.get('description'), start, end)
        if not new_event.is_valid_model():
            abort(500)
        new_event.save_to_db()
        return "Done"
    except ValueError:
        abort(500)


@app.route('/admin/event/edit/<uuid:event_id>', methods=['GET'])
@secure("events")
def event_edit_get(event_id):
    try:
        event = Event.get_by_id(event_id)
        return render_template('event_edit.html', event=event.to_json())
    except NoSuchEventExistException:
        abort(404)


@app.route('/admin/event', methods=['PUT'])
@secure("events")
def event_edit_put():
    try:
        start = datetime.strptime(request.form.get('start'), '%m/%d/%Y %I:%M %p')
        end = datetime.strptime(request.form.get('end'), '%m/%d/%Y %I:%M %p')
        new_event = Event(request.form.get('title'),
                          request.form.get('description'),
                          start,
                          end,
                          uuid.UUID(request.form.get('id')))
        if not new_event.is_valid_model():
            abort(500)
        new_event.sync_to_db()
        return "Done"
    except ValueError:
        abort(500)


@app.route('/admin/event/<uuid:event_id>', methods=['DELETE'])
@secure("events")
def event_delete_delete(event_id):
    try:
        old_event = Event.get_by_id(event_id)
        old_event.remove_from_db()
        return jsonify({"message": "Done"}), 200
    except NoSuchEventExistException:
        abort(404)


@app.route('/event/<uuid:event_id>', methods=['GET'])
def event_get(event_id):
    try:
        old_event = Event.get_by_id(event_id)
        registered = None
        if session.contains('email') and session['email'] is not None:
            registered = EventRegister.check_if_registered(session['email'], event_id)
        return render_template('event.html', event=old_event.to_json(), registered=registered)
    except NoSuchEventExistException:
        abort(404)


@app.route('/admin/articles', methods=['GET'])
@secure("articles")
def articles_get_admin():
    news = [article for article in Database.find("articles", {})]
    return render_template('articles_admin.html', news=news)


@app.route('/admin/article/add', methods=['GET'])
def article_add_get():
    try:
        return render_template('article_add.html')
    except NoSuchArticleExistException:
        abort(404)


@app.route('/admin/article', methods=['POST'])
@secure("articles")
def article_add_post ():
    try:
        article_date = datetime.strptime(request.form.get('date'), '%m/%d/%Y %I:%M %p')
        new_article = None
        if request.form.get('publication') is "":
            new_article = Article(request.form.get('title'), request.form.get('summary'), article_date)
        else:
            new_article = Article(request.form.get('title'), request.form.get('summary'), article_date, request.form.get('publication'))
        if not new_article.is_valid_model():
            abort(500)
        new_article.save_to_db()
        return jsonify({"message": "Done"}), 200
    except ValueError:
        abort(500)


@app.route('/admin/article/edit/<uuid:article_id>', methods=['GET'])
def article_edit_get(article_id):
    try:
        old_article = Article.get_by_id(article_id)
        return render_template('article_edit.html', article=old_article.to_json())
    except NoSuchArticleExistException:
        abort(404)


@app.route('/admin/article', methods=['PUT'])
@secure("articles")
def article_edit_put():
    try:
        article_date = datetime.strptime(request.form.get('date'), '%m/%d/%Y %I:%M %p')
        if request.form.get('publication') is "":
            new_article = Article(request.form.get('title'),
                                  request.form.get('summary'),
                                  article_date,
                                  None,
                                  uuid.UUID(request.form.get('id')))
        else:
            new_article = Article(request.form.get('title'),
                      request.form.get('summary'),
                      article_date,
                      request.form.get('publication'),
                      uuid.UUID(request.form.get('id')))
        if not new_article.is_valid_model():
            abort(500)
        new_article.sync_to_db()
        return jsonify({"message": "Done"}), 200
    except ValueError:
        abort(500)


@app.route('/article/<uuid:article_id>', methods=['DELETE'])
@secure("articles")
def article_delete(article_id):
    try:
        old_article = Article.get_by_id(article_id)
        old_article.remove_from_db()
        return jsonify({"message": "Done"}), 200
    except NoSuchArticleExistException:
        abort(404)


@app.route('/article/<uuid:article_id>', methods=['GET'])
def article_get(article_id):
    try:
        old_article = Article.get_by_id(article_id)
        return render_template('article.html', article=old_article.to_json())
    except NoSuchArticleExistException:
        abort(404)


@app.route('/auth/login', methods=["POST"])
def login_user():
    user_email = request.form['email']
    user_password = request.form['password']

    if User.check_login(user_email, user_password):
        session['email'] = user_email
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login_page', error_message="Your username or password was incorrect."))


@app.route('/auth/register', methods=["POST"])
def register_user():
    user_email = request.form['email']
    user_password = request.form['password']

    if User.register_user(user_email, user_password):
        return redirect(url_for('index'))
    else:
        return redirect(url_for('register_page', error_message="User exists"))


@app.route('/view-profile')
@secure("user")
def view_profile():
    if session.contains('email') and session['email'] is not None:
        profile = User.find_by_email(session['email'])
        events = profile.get_registered_events(session['email'])
        totalpoints = profile.total_points()
        return render_template('user-profile.html', profile=profile, events=events, totalpoints=totalpoints, rank=profile.get_point_rank())
    else:
        return render_template('user-profile.html', message="Not Logged In")


@app.route('/user/edit-profile', methods=["POST"])
@secure("user")
def edit_profile():
    if User.check_login(session['email'], request.form['password']):
        user = User.find_by_email(session['email'])
        user.data.update(firstname=request.form['firstname'], lastname=request.form['lastname'],
                         university=request.form['university'], level=request.form['level'],
                         country=request.form['country'], school=request.form['school'],
                         subject=request.form['subject'], year=request.form['yearofstudy'])

        user.save_to_db()
        return make_response(view_profile())
    else:
        return render_template('user-profile.html', message="Incorrect Password")


@app.route('/event/signup/<uuid:event_id>', methods=['GET'])
@secure('user')
def event_signup(event_id):
    if EventRegister.check_if_registered(session['email'], event_id) is None:
        try:
            EventRegister.register_for_event(session['email'], event_id)
            return make_response(event_get(event_id))
        except NoSuchEventExistException:
            abort(404)
    else:
        EventRegister.unregister_for_event(session['email'], event_id)
        return make_response(event_get(event_id))


@app.route('/user-list')
@secure("admin")
def load_user_list():
    if User.get_user_permissions(session['email']) == 'admin':
        users = User.get_user_list()
        return render_template("admin-user-list.html", users=users)
    else:
        abort(500)


@app.route('/view-profile/<user_email>', methods=["GET"])
@secure("admin")
def admin_view_profile(user_email):
    if session.contains('email') and session['email'] is not None:
        if User.get_user_permissions(session['email']) == 'admin':
            profile = User.find_by_email(user_email)
            events = profile.get_registered_events(profile.email)
            totalpoints = profile.total_points()
            return render_template('user-profile.html', profile=profile, events=events, totalpoints=totalpoints, rank=profile.get_point_rank())

    else:
        abort(401)


@app.route('/edit-profile')
def edit_profile_page():
    return render_template('edit-profile.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/register')
def register_page():
    return render_template('register.html')


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.before_first_request
def initdb():
    get_db()
    assert Database.DATABASE is not None, "Database#initialize was called but Database.DATABASE is still None."


if __name__ == '__main__':
    app.run(debug=True, port=4999)
