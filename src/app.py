from werkzeug.exceptions import abort
from src.common.database import Database
from src.models.article import Article, NoSuchArticleExistException
from src.models.event import Event, NoSuchEventExistException
from src.models.user import User
from flask import Flask, session, jsonify, request, render_template, redirect, url_for
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
        data = render_template('layout.html', data=data)
        response.set_data(data)
        return response
    return response


@app.route('/admin/events', methods=['GET'])
def events_get_admin():
    events = [event for event in Database.find("events", {})]
    return render_template('events_admin.html', events=events)


@app.route('/admin/articles', methods=['GET'])
def articles_get_admin():
    news = [article for article in Database.find("articles", {})]
    return render_template('articles_admin.html', news=news)


@app.route('/event', methods=['POST'])
def event_post():
    try:
        event_date = datetime.strptime(request.form.get('date'), '%m/%d/%Y %I:%M %p')

        new_event = Event(request.form.get('title'), request.form.get('description'), event_date)
        if not new_event.is_valid_model():
            abort(500)
        new_event.save_to_db()
        return "Done"
    except ValueError:
        abort(500)


@app.route('/event', methods=['PUT'])
def event_put():
    try:
        trff = request.form.get('description')
        event_date = datetime.strptime(request.form.get('date'), '%m/%d/%Y %I:%M %p')
        new_event = Event(request.form.get('title'),
                          request.form.get('description'),
                          event_date,
                          uuid.UUID(request.form.get('id')))
        if not new_event.is_valid_model():
            abort(500)
        new_event.sync_to_db()
        return "Done"
    except ValueError:
        abort(500)


@app.route('/event/<uuid:event_id>', methods=['DELETE'])
def event_delete(event_id):
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
        return render_template('event.html', event=old_event)
    except NoSuchEventExistException:
        abort(404)


@app.route('/article', methods=['POST'])
def article_post():
    try:
        article_date = datetime.strptime(request.form.get('date'), '%m/%d/%Y %I:%M %p')

        new_article = Article(request.form.get('title'), request.form.get('summary'), article_date)
        if not new_article.is_valid_model():
            abort(500)
        new_article.save_to_db()
        return jsonify({"message": "Done"}), 200
    except ValueError:
        abort(500)


@app.route('/article', methods=['PUT'])
def article_put():
    try:
        article_date = datetime.strptime(request.form.get('date'), '%m/%d/%Y %I:%M %p')

        new_article = Article(request.form.get('title'),
                            request.form.get('summary'),
                            article_date,
                            uuid.UUID(request.form.get('id')))
        if not new_article.is_valid_model():
            abort(500)
        new_article.sync_to_db()
        return jsonify({"message": "Done"}), 200
    except ValueError:
        abort(500)



@app.route('/article/<uuid:article_id>', methods=['DELETE'])
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
        return render_template('article.html', article=old_article)
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
def view_profile():
    if session.contains('email') and session['email'] is not None:
        profile = User.find_by_email(session['email'])
        return render_template('user-profile.html', profile=profile)
    else:
        return render_template('user-profile.html', message="Not Logged In")


@app.route('/user/edit-profile', methods=["POST"])
def edit_profile():
    if session.get('email'):
        if User.check_login(session.get('email'), request.form['password']):
            user = User.find_by_email(session['email'])
            user.data.update(firstname=request.form['firstname'], lastname=request.form['lastname'],
                             university=request.form['university'], level=request.form['level'],
                             country=request.form['country'], school=request.form['school'],
                             subject=request.form['subject'], year=request.form['yearofstudy'])

            user.save_to_db()
            return render_template(url_for('view_profile', message="Profile updated"))
        else:
            return render_template('user-profile.html', message="Incorrect Password")
    else:
        return render_template('user-profile.html', message="Not Logged In")


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
