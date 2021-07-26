from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    vitals = db.relationship('Vital', backref='user', lazy=True)


    def __repr__(self):
        return '<User %r,%r,%r>' % (self.id, self.username, self.email)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            # "favorites": [favorite.serialize() for favorite in self.favorites]
            # do not serialize the password, its a security breach
        }

class Vital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), db.ForeignKey('user.username'))

    def __repr__(self):
        return '<Favorite %r,%r,%r,%r,%r>' % (self.id, self.entity_type, self.entity_name, self.entity_id,  self.username, self.username)

    def serialize(self):
        return {
            "id": self.id,
            # "username": self.username,
            "username": self.username,

            # do not serialize the password, its a security breach
        }

# class Symptom(db.Model):


# class Medicine(db.Model):

