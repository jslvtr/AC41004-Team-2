__author__ = 'jslvtr'

from flask import Flask, session, jsonify
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
app.secret_key = "ajfjfBafbaf1565~/?"


@app.route('/')
def index():
    if 'tmp' in session.keys():
        return jsonify({"message": session['tmp']}), 200
    else:
        session['tmp'] = "You are logged in!"
        return jsonify({"message": "empty"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=4999)
