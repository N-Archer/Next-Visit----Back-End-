"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

@app.route("/login", methods=["POST"])
def log_in():
    # username = request.json.get("username", None)
    credentials = request.get_json()
    username = credentials.get ("username", None)
    # password = request.json.get("password", None)
    password = credentials.get ("password", None)
    # Query your database for username and password
    user = User.query.filter_by(username=username, password=password).first()
    if user is None:
        # the user was not found on the database
        return jsonify({"msg": "Bad username or password"}), 401
    
    # create a new token with the user id inside
    expires = datetime.timedelta(days=7)
    access_token = create_access_token(identity=user.username, expires_delta=expires)
    return jsonify({ "token": access_token, "user_id": user.username })

@app.route('/auth', methods=['GET'])
@jwt_required()
def run_auth():
    current_user_id = get_jwt_identity()

    return jsonify(user=current_user_id), 20

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users))
    response_body = {
        "users": all_users
    }

    return jsonify(response_body), 200

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

