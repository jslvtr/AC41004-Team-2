import base64
from functools import wraps
import pymongo
from werkzeug.exceptions import abort
from src.common.constants import Constants
from src.common.database import Database
from src.common.utils import Utils
from src.models.article import Article, NoSuchArticleExistException
from src.models.award import Award
from src.models.event import Event, NoSuchEventExistException
from src.models.eventregister import EventRegister
from src.models.image import Image
from src.models.page import Page, NoSuchPageExistException

from src.models.permissions import Permissions
from src.models.university import University
from src.models.point_type import PointType
from src.models.quiz import Quiz
from src.models.quiz_profile import QuizProfile, NoSuchQuizProfileExistException
from src.models.quiz_question import NoSuchQuizQuestionExistException
from src.models.user import User
from flask import Flask, session, jsonify, request, render_template, redirect, url_for, make_response, send_file, \
    Response
from src.common.sessions import MongoSessionInterface
import os
import uuid
from time import mktime as mktime
from datetime import datetime

__author__ = 'jslvtr and stamas01 and jkerr123'

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
    news = [article for article in Database.find("articles",
                                                 {"page_id": uuid.UUID('{00000000-0000-0000-0000-000000000000}')},
                                                 sort='date',
                                                 direction=pymongo.DESCENDING,
                                                 limit=3)]
    events = [event for event in Database.find("events", {}, sort='start', direction=pymongo.DESCENDING, limit=3)]

    for article in news:
        article['summary'] = Utils.clean_for_homepage(article['summary'])
    for event in events:
        event['description'] = Utils.clean_for_homepage(event['description'])

    return render_template('home.html',
                           events=events,
                           news=news)


@app.route('/news/<uuid:page_id>')
@app.route('/news/')
def news_page(page_id=None):
    if page_id is None:
        page_id = uuid.UUID('{00000000-0000-0000-0000-000000000000}')
    news = [article for article in Database.find("articles",
                                                 {"page_id": page_id},
                                                 sort='date',
                                                 direction=pymongo.DESCENDING)]

    for article in news:
        article['summary'] = Utils.clean_for_homepage(article['summary'])

    return render_template('news.html',
                           news=news)


@app.route('/events')
def events_page():
    events = [event for event in Database.find("events", {}, sort='start', direction=pymongo.DESCENDING)]
    for event in events:
        event['id'] = str(event['_id'])
        del event['_id']
        event['title'] = "{} from {} until {}".format(event['title'],
                                                      event['start'].strftime("{}%H:%M".format(
                                                          "%d %b " if event['start'].day != event['end'].day else "")),
                                                      event['end'].strftime("{}%H:%M".format(
                                                          "%d %b " if event['start'].day != event['end'].day else "")))
        event['start'] = int(mktime(event['start'].timetuple())) * 1000
        event['end'] = int(mktime(event['end'].timetuple())) * 1000
        event['url'] = "/event/{}".format(event['id'])

    return render_template('items/events.html',
                           events=events)


@app.route('/events-list')
def events_list_page():
    events = [event for event in Database.find("events", {}, sort='start', direction=pymongo.DESCENDING)]

    for event in events:
        event['description'] = Utils.clean_for_homepage(event['description'])

    return render_template('items/events-list.html',
                           events=events)


@app.before_first_request
def init_db():
    Database.initialize(mongodb_user, mongodb_password, mongo_url, int(mongo_port), mongo_database)


@app.after_request
def layout(response):
    if response.content_type == 'text/html; charset=utf-8' and 'static/' not in request.base_url:
        data = response.get_data()
        data = data.decode('utf-8')
        pages = Page.get_all()
        pages_json = []
        for page in pages:
            pages_json.append(page.to_json())
        if str(request.url_rule).startswith("/admin"):
            data = render_template('admin.html', access_level=get_access_level(), pages=pages_json, data=data,
                                   user=session['email'] if session.contains('email') and session[
                                                                                              'email'] is not None else None)
            data = render_template('layout.html', access_level=get_access_level(), pages=pages_json, data=data,
                                   user=session['email'] if session.contains('email') and session[
                                                                                              'email'] is not None else None)
        else:
            data = render_template('layout.html', access_level=get_access_level(), pages=pages_json, data=data,
                                   user=session['email'] if session.contains('email') and session[
                                                                                              'email'] is not None else None)
        response.set_data(data)
        response.direct_passthrough = False

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
    for event in events:
        del event['description']
    return render_template('items/events_admin.html', events=events)


@app.route('/admin/upload', methods=['POST'])
@secure("events")
def upload_image():
    file_data = request.files['file']
    image = Image(file_data.read(), file_data.mimetype)
    image.save_to_db()
    return jsonify({"id": image.get_id()}), 200


@app.route('/images/<uuid:image_id>', methods=['GET'])
def images(image_id):
    image = Image.get_by_id(image_id)
    fr = make_response(image.get_data())
    fr.headers['Content-Type'] = image.get_content_type()
    return fr


@app.route('/admin/permissions', methods=['GET'])
@secure("admin")
def permissions_get_admin():
    permissions = [permission_level for permission_level in Database.find(Permissions.COLLECTION, {})
                   if not("admin" == permission_level.get("name"))]

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
    if name != "":
        permission = Permissions(name, access)
        permission.save_to_db()

        return jsonify({"message": "ok"}), 201
    else:
        return jsonify({"error": "please enter a value"}), 201


@app.route('/admin/point_types', methods=['GET'])
@secure("admin")
def point_types_get_admin():
    point_types = [type for type in Database.find(PointType.COLLECTION, {})]
    point_types_objects = []
    for type in point_types:
        del type['_id']
        type_obj = PointType(**type)
        type_obj.total = type_obj.users_with_point()
        point_types_objects.append(type_obj)

    return render_template('admin-point-types.html', point_types=point_types_objects)


@app.route('/admin/point_types/<string:name>', methods=['DELETE'])
@secure("admin")
def remove_point_type(name):
    PointType.find_by_name(name).remove_from_db()
    return jsonify({"message": "ok"}), 200


@app.route('/admin/point_types', methods=['POST'])
@secure("admin")
def add_point_type():
    json = request.get_json()
    name = json['name']

    point_type = PointType(name)
    point_type.save_to_db()

    return jsonify({"message": "ok"}), 201


@app.route('/admin/event/add/', methods=['GET'])
@secure("events")
def event_add_get():
    try:
        return render_template('items/event_edit.html',
                               event=Event("", "", "", "", datetime.now(), datetime.now()).to_json(), action_type="Add",
                               event_types=Constants.EVENT_TYPES)
    except NoSuchEventExistException:
        abort(404)


@app.route('/admin/event', methods=['POST'])
@secure("events")
def event_add_post():
    try:
        start = datetime.strptime(request.form.get('start'), '%m/%d/%Y %I:%M %p')
        end = datetime.strptime(request.form.get('end'), '%m/%d/%Y %I:%M %p')
        new_event = Event(request.form.get('title'),
                          request.form.get('description'),
                          request.form.get('event_type'),
                          int(request.form.get('points')),
                          start,
                          end)
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
        return render_template('items/event_edit.html', event=event.to_json(), action_type="Edit",
                               event_types=Constants.EVENT_TYPES)
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
                          request.form.get('event_type'),
                          int(request.form.get('points')),
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
        date = datetime.now()
        ff = old_event._end < date
        return render_template('items/event.html', event=old_event.to_json(), registered=registered, date=date)
    except NoSuchEventExistException:
        abort(404)


@app.route('/admin/articles/<uuid:page_id>', methods=['GET'])
@secure("articles")
def articles_get_admin(page_id):
    news = [article for article in Database.find("articles", {'page_id': page_id})]
    for article in news:
        del article['summary']
    return render_template('items/articles_admin.html', news=news, page_id=page_id)


@app.route('/admin/article/add/<uuid:page_id>', methods=['GET'])
def article_add_get(page_id):
    try:
        return render_template('items/article_edit.html', article=Article("", "", datetime.now(), page_id).to_json(),
                               action_type="Add")
    except NoSuchArticleExistException:
        abort(404)


@app.route('/admin/article/', methods=['POST'])
@secure("articles")
def article_add_post():
    try:
        article_date = datetime.strptime(request.form.get('date'), '%m/%d/%Y %I:%M %p')
        new_article = None
        if request.form.get('publication') is "":
            new_article = Article(request.form.get('title'), request.form.get('summary'), article_date,
                                  uuid.UUID(request.form.get('page_id')), )
        else:
            new_article = Article(request.form.get('title'), request.form.get('summary'), article_date,
                                  uuid.UUID(request.form.get('page_id')),
                                  request.form.get('publication'))
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
        return render_template('items/article_edit.html', article=old_article.to_json(), action_type="Edit")
    except NoSuchArticleExistException:
        abort(404)


@app.route('/admin/article/', methods=['PUT'])
@secure("articles")
def article_edit_put():
    try:
        article_date = datetime.strptime(request.form.get('date'), '%m/%d/%Y %I:%M %p')
        if request.form.get('publication') is "":
            new_article = Article(request.form.get('title'),
                                  request.form.get('summary'),
                                  article_date,
                                  uuid.UUID(request.form.get('page_id')),
                                  None,
                                  uuid.UUID(request.form.get('id')))
        else:
            new_article = Article(request.form.get('title'),
                                  request.form.get('summary'),
                                  article_date,
                                  uuid.UUID(request.form.get('page_id')),
                                  request.form.get('publication'),
                                  uuid.UUID(request.form.get('id')))
        if not new_article.is_valid_model():
            abort(500)
        new_article.sync_to_db()
        return jsonify({"message": "Done"}), 200
    except ValueError:
        abort(500)


@app.route('/admin/article/<uuid:article_id>', methods=['DELETE'])
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
        return render_template('items/article.html', article=old_article.to_json())
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
        session['email'] = user_email
        return redirect(url_for('index'))
    else:
        return redirect(url_for('register_page', error_message="User exists"))


@app.route('/view-profile')
@secure("user")
def view_profile():
    if session.contains('email') and session['email'] is not None:
        profile = User.find_by_email(session['email'])
        events = profile.get_registered_events(session['email'])
        attended_events = profile.get_all_attended(session['email'])
        current_date = datetime.now()
        #current_date = current_date.strftime("%d-%m-%Y at %H:%M")
        totalpoints = profile.total_points()
        user_points = profile.data['points'] if 'points' in profile.data.keys() else None
        awards = []
        if user_points is not None:
            awards = Award.check_user_awards(profile.data['points'])

        return render_template('user-profile.html', profile=profile, events=events, attended_events=attended_events, totalpoints=totalpoints,
                               rank=profile.get_point_rank(), awards=awards, date=current_date)
    else:
        return render_template('user-profile.html', message="Not Logged In")


@app.route('/user/edit-profile', methods=["POST"])
@secure("user")
def edit_profile():
    if User.check_login(session['email'], request.form['password']):
        user = User.find_by_email(session['email'])
        user.data.update(firstname=request.form['firstname'], lastname=request.form['lastname'],
                         university=request.form['university'], level=request.form['level'],
                         country=request.form['country'], school=request.form['college'],
                         subject=request.form['course'], year=request.form['yearofstudy'])

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


@app.route('/admin/user-list')
@secure("admin")
def load_user_list():
    if User.get_user_permissions(session['email']) == 'admin':
        users = User.get_user_list()
        return render_template("admin-user-list.html", users=users)
    else:
        abort(500)


@app.route('/admin/view-profile/<user_email>', methods=["GET"])
@secure("admin")
def admin_view_profile(user_email):
    if session.contains('email') and session['email'] is not None:
        if User.get_user_permissions(session['email']) == 'admin':
            profile = User.find_by_email(user_email)
            events = profile.get_registered_events(profile.email)
            totalpoints = profile.total_points()
            attended_events = profile.get_all_attended(profile.email)
            current_date = datetime.now()
            permissions = User.get_user_permissions(session['email'])
            user_points = profile.data['points'] if 'points' in profile.data.keys() else None
            awards = []
            if user_points is not None:
                awards = Award.check_user_awards(profile.data['points'])
            return render_template('user-profile.html', email=user_email, profile=profile, events=events, totalpoints=totalpoints,
                                   rank=profile.get_point_rank(), permissions=permissions, date=current_date,
                                   attended_events=attended_events, awards=awards)

    else:
        abort(401)


@app.route('/admin/export-users/export', methods=["POST"])
@secure("admin")
def export_users():
    country = request.form['country']
    query_builder = {}
    if country != "None" and country != "":
        query_builder.update({"country": country})
    university = request.form['university']
    if university != "None" and university != "":
        query_builder.update({"university": university})
    college = request.form['college']
    if college != "None" and college != "":
        query_builder.update({"school": college})
    subject = request.form['course']
    if subject != "None" and subject != "":
        query_builder.update({"subject": subject})
    level = request.form['level']
    if level != "None":
        query_builder.update({"level": level})
    year = request.form['yearofstudy']
    if year != "None":
        query_builder.update({"year": year})

    action = request.form['action']
    if action != "":
        action_points = int(action)
        if action_points != "":
            action_operator = request.form['action-operator']
            if action_operator == ">":
                query_builder.update({"points.action": {"$gt": action_points}})
            elif action_operator == "<":
                query_builder.update({"points.action": {"$lt": action_points}})
            elif action_operator == "=":
                query_builder.update({"points.action": action_points})

    networking = request.form['networking']
    if networking != "":
        networking_points = int(networking)
        if networking_points != "":
            networking_operator = request.form['networking-operator']
            if networking_operator == ">":
                query_builder.update({"points.networking": {"$gt": networking_points}})
            elif networking_operator == "<":
                query_builder.update({"points.networking": {"$lt": networking_points}})
            elif networking_operator == "=":
                query_builder.update({"points.networking": networking_points})

    practice = request.form['practice']
    if practice != "":
        practice_points = int(request.form['practice'])
        if practice_points != "":
            practice_operator = request.form['practice-operator']
            if practice_operator == ">":
                query_builder.update({"points.practice": {"$gt": practice_points}})
            elif practice_operator == "<":
                query_builder.update({"points.practice": {"$lt": practice_points}})
            elif practice_operator == "=":
                query_builder.update({"points.practice": practice_points})

    project = request.form['project']
    if project != "":
        project_points = int(request.form['project'])
        if project_points != "":
            project_operator = request.form['project-operator']
            if project_operator == ">":
                query_builder.update({"points.project": {"$gt": project_points}})
            elif project_operator == "<":
                query_builder.update({"points.project": {"$lt": project_points}})
            elif project_operator == "=":
                query_builder.update({"points.project": project_points})

    theory = request.form['theory']
    if theory != "":
        theory_points = int(request.form['theory'])
        if theory_points != "":
            theory_operator = request.form['theory-operator']
            if theory_operator == ">":
                query_builder.update({"points.theory": {"$gt": theory_points}})
            elif theory_operator == "<":
                query_builder.update({"points.theory": {"$lt": theory_points}})
            elif theory_operator == "=":
                query_builder.update({"points.theory": theory_points})

    virtual = request.form['virtual']
    if virtual != "":
        virtual_points = int(request.form['virtual'])
        if virtual_points != "":
            virtual_operator = request.form['virtual-operator']
            if virtual_operator == ">":
                query_builder.update({"points.virtual": {"$gt": virtual_points}})
            elif virtual_operator == "<":
                query_builder.update({"points.virtual": {"$lt": virtual_points}})
            elif virtual_operator == "=":
                query_builder.update({"points.virtual": virtual_points})

    users = User.get_by_filtering(query_builder)
    users_csv = User.export_to_csv(users)
    return Response(users_csv, headers={"Content-Disposition": "attachment; filename=userlist.csv"},
                    content_type="text/csv")

@app.route('/admin/export-users')
@secure("admin")
def show_export_users():
    universities = University.get_uni_list()
    return render_template("user-export.html", universities=universities)



@app.route('/admin/event/registrations/<uuid:event_id>', methods=['GET'])
@secure("admin")
def view_event_registrations(event_id):
    if session.contains('email') and session['email'] is not None:
        if User.get_user_permissions(session['email']) == 'admin':
            users = EventRegister.list_registered_users(event_id)
            return render_template('admin-event-registrations.html', users=users, event_id=event_id)
        else:
            abort(401)


@app.route('/admin/update-attended/<user>/<event_id>', methods=['GET'])
def update_attended(user, event_id):
    id_ = uuid.UUID(event_id)
    event = Event.get_by_id(id_)
    category = event.get_event_type()
    points = event.get_points()

    if EventRegister.get_user_attended(user, event_id):
        EventRegister.set_user_attended(user, event_id)
        User.update_user_points(user, category, -points)
    else:
        User.update_user_points(user, category, points)
        EventRegister.set_user_attended(user, event_id)

    return jsonify({"message": "ok"}), 200


@app.route('/edit-profile')
def edit_profile_page():
    universities = University.get_uni_list()
    profile = User.find_by_email(session['email'])
    return render_template('edit-profile.html', universities=universities, profile=profile)


@app.route('/admin/edit-profile/<user>', methods=["GET"])
@secure("admin")
def admin_edit_profile_page(user):
    universities = University.get_uni_list()
    profile = User.find_by_email(user)
    mypermissions = User.get_user_permissions(session['email'])
    permissions = [permission_level for permission_level in Database.find(Permissions.COLLECTION, {})]
    return render_template('edit-profile.html', user=user, universities=universities, profile=profile,
                           permissions=permissions, mypermissions=mypermissions)


@app.route('/admin/user/edit-profile', methods=["POST"])
@secure("admin")
def admin_update_user_profile():
    if User.check_login(session['email'], request.form['password']):
        user = User.find_by_email(request.form['email'])
        user.data.update(firstname=request.form['firstname'], lastname=request.form['lastname'],
                         university=request.form['university'], level=request.form['level'],
                         country=request.form['country'], school=request.form['college'],
                         subject=request.form['course'], year=request.form['yearofstudy'],
                         permissions=request.form['permissions'])

        user.save_to_db()
        return redirect("/admin/view-profile/" + request.form['email'])
    else:
        return render_template('user-profile.html', message="Incorrect Password")


@app.route('/populate-colleges/<university>', methods=["GET"])
def populate_colleges(university):
    university = University.get_uni(university)
    colleges = [college['name'] for college in university['colleges']]
    return jsonify({"colleges": colleges})


@app.route('/populate-courses/<university>/<college>', methods=["GET"])
def populate_courses(university, college):
    college = University.get_college(university, college)
    courses = [course for course in college['courses']]
    return jsonify({"courses": courses})


@app.route('/admin/edit-universities')
@secure("admin")
def edit_uni_page():
    if session.contains('email') and session['email'] is not None:
        if User.get_user_permissions(session['email']) == 'admin':
            universities = University.get_uni_list()
            return render_template('university-update.html', universities=universities)

    else:
        abort(401)


@app.route('/add-uni', methods=["POST"])
@secure("admin")
def add_university():
    json = request.get_json()
    uni = json['uni']
    if University.get_uni(uni):
        return jsonify({"error": "University already exists"}), 201
    University.add_university(uni)
    return jsonify({"message": "OK"}), 201


@app.route('/remove-uni/<university>', methods=["DELETE"])
@secure("admin")
def remove_university(university):
    University.delete_university(university)
    return jsonify({"message": "OK"}), 200


@app.route('/add-college', methods=["POST"])
@secure("admin")
def add_college():
    json = request.get_json()
    uni = json['uni']
    college = json['college']
    if University.get_college(uni, college):
        return jsonify({"error": "College already exists"}), 201
    University.add_college(uni, college)
    return jsonify({"message": "OK"}), 201


@app.route('/remove-college/<university>/<college>', methods=["DELETE"])
@secure("admin")
def remove_college(university, college):
    University.delete_college(university, college)
    return jsonify({"message": "OK"}), 200


@app.route('/add-course', methods=["POST"])
@secure("admin")
def add_course():
    json = request.get_json()
    uni = json['uni']
    college = json['college']
    course = json['course']
    if University.get_course(uni, college, course):
        return jsonify({"error": "Course already exists"}), 201
    University.add_course(uni, college, course)
    return jsonify({"message": "OK"}), 201


@app.route('/remove-course/<university>/<college>/<course>', methods=["DELETE"])
@secure("admin")
def remove_course(university, college, course):
    University.delete_course(university, college, course)
    return jsonify({"message": "OK"}), 200


@app.route('/check-password', methods=["POST"])
def check_password():
    json = request.get_json()
    password = json['password']
    if User.check_login(session['email'], password):
        return jsonify({"message": "OK"}), 201
    return jsonify({"error": "Password is incorrect"}), 201



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


@app.route('/admin/designer', methods=['GET'])
@secure("admin")
def designer():
    pages = Page.get_all()
    pages_json = []
    active_page = None
    for page in pages:
        if page is pages[0]:
            active_page = pages[0].to_json()
        pages_json.append(page.to_json())
    return render_template('designer/main.html', pages=pages_json, active_page=active_page)


@app.route('/admin/designer/add', methods=['GET'])
@secure("admin")
def designer_add_get():
    pages = Page.get_all()
    pages_json = []
    active_page = Page("", "")
    for page in pages:
        pages_json.append(page.to_json())
    return render_template('designer/main.html', pages=pages_json, active_page=active_page)


@app.route('/admin/designer/<title>', methods=['GET'])
@secure("admin")
def designer_s(title=None):
    pages = Page.get_all()
    pages_json = []
    active_page = None
    for page in pages:
        if page.get_title() == title:
            active_page = page.to_json()
        pages_json.append(page.to_json())
    return render_template('designer/main.html', pages=pages_json, active_page=active_page)


@app.route('/admin/page/add/', methods=['POST'])
@secure("admin")
def designer_add():
    page = Page(request.form.get('title'),
                request.form.get('content'),
                bool(request.form.get('feed')),
                bool(request.form.get('active')))
    if not page.is_valid_model():
        return jsonify({"result": "error", "field": "", "message": "Unknown Error"}), 200

    if len(page.get_title()) == 0:
        return jsonify({"result": "error", "field": "title", "message": "Title cannot be empty!"}), 200
    if page.is_there_any_with_title(page.get_title()):
        return jsonify({"result": "error", "field": "title", "message": "Title has to be unique!"}), 200
    page.save_to_db()

    return jsonify({"result": "ok", "field": "title", "message": ""}), 200


@app.route('/admin/page/edit/', methods=['PUT'])
@secure("admin")
def designer_edit():
    page = Page(request.form.get('title'),
                request.form.get('content'),
                bool(request.form.get('feed')),
                bool(request.form.get('active')),
                uuid.UUID(request.form.get('id')))
    if not page.is_valid_model():
        return jsonify({"result": "error", "field": "", "message": "Unknown Error"}), 200

    if len(page.get_title()) == 0:
        return jsonify({"result": "error", "field": "title", "message": "Title cannot be empty!"}), 200
    page.sync_to_db()

    return jsonify({"result": "ok", "field": "title", "message": ""}), 200


@app.route('/page/<title>', methods=['GET'])
def get_page(title):
    try:
        page = Page.get_by_title(title)
        news = []
        if page.get_feed():
            news = [article for article in Database.find("articles",
                                                         {"page_id": page.get_id()},
                                                         sort='date',
                                                         direction=pymongo.DESCENDING,
                                                         limit=3)]
            for article in news:
                article['summary'] = Utils.clean_for_homepage(article['summary'])
        return render_template('page.html', page=page.to_json(), news=news)
    except NoSuchPageExistException as e:
        abort(401)


@app.route('/admin/page/<uuid:page_id>', methods=['DELETE'])
@secure("admin")
def page_delete(page_id):
    try:
        old_page = Page.get_by_id(page_id)
        old_page.remove_from_db()
        return jsonify({"message": "Done"}), 200
    except NoSuchPageExistException:
        abort(404)


@app.route('/quizzes', methods=['GET'])
@secure("user")
def get_quizzes_view():
    quizzes = Quiz.get_all()
    quizzes_json = []
    for quiz in quizzes:
        quizzes_json.append(quiz.to_json())
    return render_template('quiz/user/list.html', quizzes=quizzes_json)


@app.route('/quiz_profile/<uuid:quiz_id>', methods=['GET'])
@secure("user")
def get_quiz_profile_view(quiz_id):
    quiz_profile = None
    try:
        quiz_profile = QuizProfile.get_by_composite_id(quiz_id,session['email'])
        return render_template('quiz/user/quiz_profile.html', quiz_profile=quiz_profile.to_json(), quiz_id=quiz_id)
    except NoSuchQuizProfileExistException as e:
       return render_template('quiz/user/quiz_profile.html', quiz_profile=None, quiz_id=quiz_id)



@app.route('/quiz/<uuid:quiz_id>', methods=['GET'])
@secure("user")
def get_quiz_view(quiz_id):
    try:
        QuizProfile.get_by_composite_id(quiz_id,session['email'])
        abort(401)
    except NoSuchQuizProfileExistException as e:
        quiz = Quiz.get_by_id(quiz_id)
        return render_template('quiz/user/quiz.html', active_quiz=quiz.to_json())


@app.route('/quiz', methods=['Post'])
@secure("user")
def submit_quiz():
    if request.get_json() is None:
        return jsonify({"result": "error", "field":"", "message": "Not valid model!"}), 200
    quiz = Quiz.factory_form_json(request.get_json())
    if quiz.get_points() is "":
        return jsonify({"result": "error", "field":"points", "message": "Points cannot be empty"}), 200
    if not quiz.is_valid_model():
        return jsonify({"result": "error", "field":"", "message": "Not valid model!"}), 200
    if len(quiz.get_title()) == 0:
        return jsonify({"result": "error", "field": "title", "message": "Title cannot be empty!"}), 200
    if quiz.get_points() < 0:
        return jsonify({"result": "error", "field":"points", "message": "Points cannot be less then 0!"}), 200
    quiz_real = Quiz.get_by_id(uuid.UUID(quiz._id))

    passed = False
    if quiz_real.mark_subbmitted_quiz(quiz):
        passed = True
    try:
        QuizProfile.get_by_composite_id(uuid.UUID(quiz._id),session['email'])
        return jsonify({"result": "ok", "field": "title", "message": "", "relocateTo": "/quiz_profile/"+str(quiz_real.get_id()) }), 200
    except NoSuchQuizProfileExistException as e:
        new_quiz_profile = QuizProfile(uuid.UUID(quiz._id),session['email'],datetime.now(),0,passed)
        new_quiz_profile.save_to_db()
        User.update_user_points(session['email'],"virtual",quiz_real.get_points())
        return jsonify({"result": "ok", "field": "title", "message": "", "relocateTo": "/quiz_profile/"+str(quiz_real.get_id())}), 200






@app.route('/admin/quizzes/<quiz_title>', methods=['GET'])
@secure("admin")
def get_admin_quizzes_view(quiz_title=None):
    quizzes = Quiz.get_all()
    quizzes_json = []
    active_quiz = None
    for quiz in quizzes:
        if quiz._title == quiz_title:
            active_quiz=quiz.to_json()
        quizzes_json.append(quiz.to_json())
    return render_template('quiz/admin/main.html', quizzes=quizzes_json, active_quiz = active_quiz)


@app.route('/admin/quizzes/add', methods=['GET'])
@secure("admin")
def get_admin_quizzes_view_add():
    quizzes = Quiz.get_all()
    quizzes_json = []
    active_quiz = None
    for quiz in quizzes:
        quizzes_json.append(quiz.to_json())
    return render_template('quiz/admin/main.html', quizzes=quizzes_json, active_quiz=None, it_is_new="True")


@app.route('/admin/quiz', methods=['POST'])
@secure("admin")
def add_quiz():
    if request.get_json() is None:
        return jsonify({"result": "error", "field":"", "message": "Not valid model!"}), 200
    quiz = Quiz.factory_form_json(request.get_json())
    if quiz.get_points() is "":
        return jsonify({"result": "error", "field":"points", "message": "Points cannot be empty"}), 200
    if not quiz.is_valid_model():
        return jsonify({"result": "error", "field":"", "message": "Not valid model!"}), 200
    if len(quiz.get_title()) == 0:
        return jsonify({"result": "error", "field": "title", "message": "Title cannot be empty!"}), 200
    if quiz.get_points() < 0:
        return jsonify({"result": "error", "field":"points", "message": "Points cannot be less then 0!"}), 200
    quiz.save_to_db()
    return jsonify({"result": "ok"}), 200


@app.route('/admin/quiz', methods=['PUT'])
@secure("admin")
def edit_quiz():
    if request.get_json() is None:
        return jsonify({"result": "error", "field":"", "message": "Not valid model!"}), 200
    quiz = Quiz.factory_form_json(request.get_json())
    if quiz.get_points() is "":
        return jsonify({"result": "error", "field":"points", "message": "Points cannot be empty"}), 200
    if not quiz.is_valid_model():
        return jsonify({"result": "error", "field":"", "message": "Not valid model!"}), 200
    if len(quiz.get_title()) == 0:
        return jsonify({"result": "error", "field":"title", "message": "Title cannot be empty!"}), 200
    if quiz.get_points() < 0:
        return jsonify({"result": "error", "field":"points", "message": "Points cannot be less then 0!"}), 200
    quiz.sync_to_db();
    return render_template('quiz/user/quiz.html', quiz=quiz)


@app.route('/admin/quiz/<uuid:quiz_id>', methods=['Delete'])
@secure("admin")
def delete_quiz(quiz_id):
    quiz = Quiz.get_by_id(quiz_id)
    quiz.remove_from_db()
    return jsonify({"result": "ok", "field": "title", "message": ""}), 200

@app.before_first_request
def initdb():
    get_db()
    assert Database.DATABASE is not None, "Database#initialize was called but Database.DATABASE is still None."


if __name__ == '__main__':
    app.run(debug=True, port=4999)
