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
from models import db, User, Vital, Medication, Symptom, SymptomNote

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

# @app.route("/login", methods=["POST"])
# def log_in():
#     # username = request.json.get("username", None)
#     credentials = request.get_json()
#     username = credentials.get ("username", None)
#     # password = request.json.get("password", None)
#     password = credentials.get ("password", None)
#     # Query your database for username and password
#     user = User.query.filter_by(username=username, password=password).first()
#     if user is None:
#         # the user was not found on the database
#         return jsonify({"msg": "Bad username or password"}), 401
    
#     # create a new token with the user id inside
#     expires = datetime.timedelta(days=7)
#     access_token = create_access_token(identity=user.username, expires_delta=expires)
#     return jsonify({ "token": access_token, "user_id": user.username })

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

@app.route('/user', methods=['POST'])
def post_member():
    new_user = request.get_json()
    # users = user.add_user(new_user)
    if new_user is None or new_user['fullname'] is None or new_user['address'] is None or new_user['email'] is None or new_user['phone'] is None or new_user['username'] is None or new_user['password'] is None:
        raise APIException("Body cannot be empty // missing input", status_code=400)
    new_user = User(fullname=new_user['fullname'], address= new_user['address'], email=new_user['email'], phone=new_user['phone'], username=new_user['username'],password=new_user['password'] )

    db.session.add(new_user)
    db.session.commit()

    response_body = {
        "added new user": "New user Added"
    }
    return jsonify(response_body), 200

@app.route('/login', methods=['POST'])
def login_user():
    new_user = request.get_json()
    # users = user.add_user(new_user)
    if new_user is None or new_user['username'] is None or new_user['password'] is None:
        raise APIException("Username / pw cannot be empty", status_code=400)

    user = User.query.filter_by(username=new_user['username'],password=new_user['password']).first()
    if not user:
        raise APIException("User does not exits" , status_code=404)
    data = {}

    heart_rate = Vital.query.filter_by(username=new_user['username'],vital_name="Heart Rate")
    weight = Vital.query.filter_by(username=new_user['username'],vital_name="Weight")
    height = Vital.query.filter_by(username=new_user['username'],vital_name='Height')
    blood_pressure = Vital.query.filter_by(username=new_user['username'],vital_name='Blood Pressure')
    medications = Medication.query.filter_by(username=new_user['username'])
    symptoms = Symptom.query.filter_by(username=new_user['username'])   

    # all_vitals = list(map(lambda x: x.serialize(), vitals))
    all_medications = list(map(lambda x: x.serialize(), medications))
    all_symptoms = list(map(lambda x: x.serialize(), symptoms))
    weight = list(map(lambda x: x.serialize(), weight))
    height = list(map(lambda x: x.serialize(), height))
    blood_pressure = list(map(lambda x: x.serialize(), blood_pressure))
    heart_rate = list(map(lambda x: x.serialize(), heart_rate))

    data['vitals']={
        "heart_rate": heart_rate,
        "weight": weight,
        "height": height,
        "blood_pressure": blood_pressure,
    }

    data['medications']=all_medications
    data['symptoms']=all_symptoms

    return jsonify(data), 200

@app.route('/vital', methods=['GET'])
def get_vitals():
    vitals = Vital.query.all()
    all_vitals = list(map(lambda x: x.serialize(), vitals))
    response_body = {
        "vitals": all_vitals
    }

    return jsonify(response_body), 200
    


@app.route('/<username>/vital', methods=["POST"])
def add_vital(username):
    request_body = request.get_json()
    new_vital = Vital(vital_name=request_body['vitalName'], date=request_body['date'], value=request_body['value'], username=username)
    db.session.add(new_vital)
    db.session.commit()
    
    vitals = Vital.query.filter_by(username=username)
    all_vitals = list(map(lambda x: x.serialize(), vitals))

    response_body = {
        "new_vital": request_body,
        "all_vitals": all_vitals
    }
    return jsonify(all_vitals), 200 

@app.route('/<username>/vital/<int:id>', methods=["DELETE"])
def delete_vital(username, id):
    deleted_vital = Vital.query.filter_by(username=username, id=id).first()
    if deleted_vital is None:
        raise APIException("Item Not Found", status_code=404)
    # vital = Vital.query.get(id)
    db.session.delete(deleted_vital)
    db.session.commit()
    
    vitals = Vital.query.filter_by(vital_name=deleted_vital.vital_name)
    all_vitals = list(map(lambda x: x.serialize(), vitals))

    response_body = {
        "all_vitals": all_vitals
    }
    return jsonify(all_vitals), 200 


@app.route('/medication', methods=['GET'])
def get_medications():
    medications = Medication.query.all()
    all_medications = list(map(lambda x: x.serialize(), medications))
    response_body = {
        "medication": all_medications
    }

    return jsonify(response_body), 200

@app.route('/<username>/medication', methods=["POST"])
def add_medication(username):
    request_body = request.get_json()
    new_medication = Medication(name=request_body['name'], dose=request_body['dose'], frequency=request_body['frequency'], reason=request_body['reason'], side_effects=request_body['sideEffects'], username=username)
    db.session.add(new_medication)
    db.session.commit()
    
    medications = Medication.query.filter_by(username=username)
    all_medications = list(map(lambda x: x.serialize(), medications))

    return jsonify(all_medications), 200 

@app.route('/<username>/medication/<int:id>', methods=["DELETE"])
def delete_medication(username, id):
    deleted_medication = Medication.query.filter_by(username=username, id=id).first()
    if deleted_medication is None:
        raise APIException("Item Not Found", status_code=404)
    # vital = Vital.query.get(id)
    db.session.delete(deleted_medication)
    db.session.commit()
    
    medications = Medication.query.filter_by(username=username)
    all_medications = list(map(lambda x: x.serialize(), medications))

    response_body = {
        "all_medications": all_medications
    }
    return jsonify(all_medications), 200 

@app.route('/symptom', methods=['GET'])
def get_symptoms():
    symptoms = Symptom.query.all()
    all_symptoms = list(map(lambda x: x.serialize(), symptoms))
    response_body = {
        "symptom": all_symptoms
    }

    return jsonify(all_symptoms), 200

@app.route('/<username>/symptom', methods=["POST"])
def add_symptom(username):
    request_body = request.get_json()
    new_symptom = Symptom(symptomName=request_body['symptomName'], startDate=request_body['startDate'], frequency=request_body['frequency'], severity=request_body['severity'], location=request_body['location'], symptom_note=request_body['notes'], username=username)
    db.session.add(new_symptom)
    db.session.commit()
    
    symptoms = Symptom.query.filter_by(username=username)
    all_symptoms = list(map(lambda x: x.serialize(), symptoms))

    return jsonify(all_symptoms), 200 

@app.route('/<username>/symptom/<int:id>', methods=["DELETE"])
def delete_symptom(username, id):
    deleted_symptom = Symptom.query.filter_by(username=username, id=id).first()
    if deleted_symptom is None:
        raise APIException("Item Not Found", status_code=404)
    # vital = Vital.query.get(id)
    db.session.delete(deleted_symptom)
    db.session.commit()
    
    symptoms = Symptom.query.filter_by(username=username)
    all_symptoms = list(map(lambda x: x.serialize(), symptoms))

    response_body = {
        "all_symptoms": all_symptoms
    }
    return jsonify(all_symptoms), 200 

# @app.route('/symptom_note', methods=['GET'])
# def get_symptom_notes():
#     symptom_notes = SymptomNote.query.all()
#     all_symptom_notes = list(map(lambda x: x.serialize(), symptom_notes))
#     response_body = {
#         "all_symptom_notes": all_symptom_notes
#     }

#     return jsonify(response_body), 200

@app.route('/<username>/<int:id>/note', methods=["POST"])
def add_symptom_note(username, id):
    request_body = request.get_json()
    new_symptom_note = SymptomNote( date=request_body['date'], severity=request_body['severity'], note=request_body['description'], symptom_id=id)
    db.session.add(new_symptom_note)
    db.session.commit()
    
    symptoms = Symptom.query.filter_by(username=username)
    all_symptoms = list(map(lambda x: x.serialize(), symptoms))

    # response_body = {
    #     "symptom_note": request_body,
    #     "all_symptoms": all_symptoms
    # }

    return jsonify(all_symptoms), 200 

# @app.route('/<username>/symptom/note/<int:id>', methods=["DELETE"])
# def delete_symptom_note(username, id):
#     deleted_symptom_note = SymptomNote.query.filter_by(username=username, id=id).first()
#     if deleted_symptom_note is None:
#         raise APIException("Item Not Found", status_code=404)
#     db.session.delete(deleted_symptom_note)
#     db.session.commit()
    
#     symptom_notes = SymptomNote.query.filter_by()
#     all_symptom_notes = list(map(lambda x: x.serialize(), symptom_notes))

#     response_body = {
#         "all_symptom_notes": all_symptom_notes
#     }
#     return jsonify(all_symptom_notes), 200 

# class SymptomNote(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.String(200), unique=True, nullable=False)	
#     symptom_id = db.Column(db.Integer, db.ForeignKey('symptom.id'))
#     note = db.Column(db.String(500), unique=False, nullable=False)	

    # id = db.Column(db.Integer, primary_key=True)
    # vitalname = db.Column(db.String(200), unique=False, nullable=False)	
    # date = db.Column(db.String(200), unique=True, nullable=False)	
    # value = db.Column(db.String(200), unique=True, nullable=False)		
    # username = db.Column(db.String(20), db.ForeignKey('user.username'))

# no ID for post method: must create separate end points for post & delete
# @app.route('/vital/<int:id>', methods=[ "DELETE" ])

# @app.route('/medication/<int:id>', methods=["POST", "DELETE"])

# @app.route('/symptom/<int:id>', methods=["POST", "DELETE"])
# def change_user(id):
#     request_body = request.get_json()
#     if request_body is None or request_body == {}:
#         raise APIException("Empty Body", status_code=404)
#     if request.method == "POST":
#         new_planet = Favorite(entity_name=request_body['entity_name'], entity_type="planet", entity_id=id, username=request_body['username'])
#         db.session.add(new_planet)
#         db.session.commit()
#     if request.method == 'DELETE':
#         deleted_planet = Favorite.query.filter_by(username=request_body["username"], entity_type="planet", entity_id=id).first()
#         if deleted_planet is None:
#             raise APIException("User Not Found", status_code=404)
#         db.session.delete(deleted_planet)
#         db.session.commit()
#     favorites = Favorite.query.filter_by(username=request_body['username'])
#     all_favorites = list(map(lambda x: x.serialize(), favorites))
#     response_body = {
#         "Favorites": all_favorites
#     }

#     return jsonify(response_body), 200 


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

