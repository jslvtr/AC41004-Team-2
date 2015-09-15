__author__ = 'jslvtr'

from flask import Flask, session, jsonify
from src.common.sessions import MongoSessionInterface

app = Flask(__name__)
app.session_interface = MongoSessionInterface(db="enterprisegym")
app.secret_key = "ajfjfBafbaf1565~/?"


@app.route('/')
def index():
    if 'tmp' in session.keys():
        return jsonify({"message": session['tmp']}), 200
    else:
        session['tmp'] = "You are logged in!"
        return jsonify({"message": "empty"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
