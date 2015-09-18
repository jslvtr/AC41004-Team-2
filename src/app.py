from src.common.database import Database
from src.models.user import User

__author__ = 'jslvtr'

from flask import Flask, session, jsonify, request, render_template, redirect, url_for
from src.common.sessions import MongoSessionInterface
import os

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

app.secret_key = os.urandom(0)


@app.route('/')
def index():
    return render_template('home.html',
                           events=[{'title': 'Freetime', 'summary': 'Have a beer'}],
                           news=[{'heading': 'Beer', 'Free beer': 'Have a beer'}])




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
    if session.get('email'):
        profile = User.get_user_profile(session['email'])
        return render_template('user-profile.html', profile=profile)
    else:
        return render_template('user-profile.html', error="Not Logged In")


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
    Database.initialize(mongodb_user, mongodb_password, mongo_url, int(mongo_port), mongo_database)

if __name__ == '__main__':
    app.run(debug=True, port=4999)
