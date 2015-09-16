from src.models.user import User

__author__ = 'jslvtr'

from flask import Flask, session, jsonify, request, redirect, url_for
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

app.secret_key = open("/dev/random", "rb").read(32)


@app.route('/')
def index():
    if 'tmp' in session.keys():
        return jsonify({"message": session['tmp']}), 200
    else:
        session['tmp'] = "You are logged in!"
        return jsonify({"message": "empty"}), 200


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
