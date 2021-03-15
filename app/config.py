from app.errors import NotFoundRequest
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_apscheduler import APScheduler
import os

MIN_FRONTEND_VERSION = 1
BACKEND_VERSION = 1

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.getenv('STORAGE_PATH', '..') + '/database.db'
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')


db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

scheduler = APScheduler()
scheduler.api_enabled = False
scheduler.init_app(app)
scheduler.start()

@app.after_request
def add_cors_headers(response):
    if not request.referrer:
        return response
    r = request.referrer[:-1]
    url = os.environ['FRONT_URL'] if 'FRONT_URL' in os.environ else None
    if url and r == url:
        response.headers.add('Access-Control-Allow-Origin', r)
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Headers', 'Cache-Control')
        response.headers.add(
            'Access-Control-Allow-Headers', 'X-Requested-With')
        response.headers.add('Access-Control-Allow-Headers', 'Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, OPTIONS, PUT, DELETE')
    return response


@app.errorhandler(Exception)
def unhandled_exception(e):
    if e is NotFoundRequest:
        return "Requested resource not found", 404
    app.logger.error(e)
    return jsonify(message="Something went wrong"), 500


@app.errorhandler(404)
def not_found(error):
    return "Requested resource not found", 404
