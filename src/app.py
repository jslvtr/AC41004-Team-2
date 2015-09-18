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

app = Flask(__name__)
app.session_interface = MongoSessionInterface(host=mongo_url,
                                              port=int(mongo_port),
                                              db=mongo_database,
                                              user=mongodb_user,
                                              password=mongodb_password)

app.secret_key = os.urandom(32)


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


@app.route('/event', methods=['POST'])
def event_post():
    try:
        event_date = datetime.strptime(request.form.get('date'), '%b %d %Y %I:%M%p')
    except ValueError:
        abort(500)
    new_event = Event(request.form.get('title'), request.form.get('description'), event_date)
    if not new_event.is_valid_model():
        abort(500)
    new_event.save_to_db()
    return "Done"


@app.route('/event', methods=['PUT'])
def event_put():
    try:
        event_date = datetime.strptime(request.form.get('date'), '%b %d %Y %I:%M%p')
    except ValueError:
        abort(500)

    new_event = Event(request.form.get('title'),
                      request.form.get('description'),
                      event_date,
                      uuid.UUID(request.form.get('id')))
    if not new_event.is_valid_model():
        abort(500)
    new_event.sync_to_db()
    return "Done"


@app.route('/event/<uuid:event_id>', methods=['DELETE'])
def event_delete(event_id):
    try:
        old_event = Event.get_by_id(event_id)
    except NoSuchEventExistException:
        abort(404)
    old_event.remove_from_db()
    return "Done"


@app.route('/event/<uuid:event_id>', methods=['GET'])
def event_get(event_id):
    try:
        old_event = Event.get_by_id(event_id)
    except NoSuchEventExistException:
        abort(404)
    return render_template('event.html',event=old_event)


@app.route('/article', methods=['POST'])
def article_post():
    try:
        article_date = datetime.strptime(request.form.get('date'), '%b %d %Y %I:%M%p')
    except ValueError:
        abort(500)
    new_article = Article(request.form.get('title'), request.form.get('summary'), article_date)
    if not new_article.is_valid_model():
        abort(500)
    new_article.save_to_db()
    return "Done"


@app.route('/article', methods=['PUT'])
def article_put():
    try:
        article_date = datetime.strptime(request.form.get('date'), '%b %d %Y %I:%M%p')
    except ValueError:
        abort(500)

    new_article = Event(request.form.get('title'),
                      request.form.get('summary'),
                      article_date,
                      uuid.UUID(request.form.get('id')))
    if not new_article.is_valid_model():
        abort(500)
    new_article.sync_to_db()
    return "Done"


@app.route('/article/<uuid:article_id>', methods=['DELETE'])
def article_delete(article_id):
    try:
        old_article = Article.get_by_id(article_id)
    except NoSuchArticleExistException:
        abort(404)
    old_article.remove_from_db()
    return "Done"


@app.route('/article/<uuid:article_id>', methods=['GET'])
def article_get(article_id):
    try:
        old_article = Article.get_by_id(article_id)
    except NoSuchArticleExistException:
        abort(404)
    return render_template('article.html',article=old_article)


@app.route('/auth/login')
def login_user():
    user_email = request.form['email']
    user_password = request.form['password']

    if User.check_login(user_email, user_password):
        session['email'] = user_email
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login', error_message="Your username or password was incorrect."))


if __name__ == '__main__':
    app.run(debug=True, port=4999)


app.jinja_env.globals.update(event_get_small=event_get_small)
app.jinja_env.globals.update(article_get_small=article_get_small)