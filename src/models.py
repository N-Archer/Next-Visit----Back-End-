from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fullname = db.Column(db.String(120), unique=False, nullable=False)
    phone = db.Column(db.String(200), unique=True, nullable=False)
    address =  db.Column(db.String(200), unique=False, nullable=False)
    vitals = db.relationship('Vital', backref='user')

    def __repr__(self):
        return '<User %r,%r,%r>' % (self.id, self.username, self.email)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "fullname": self.fullname,
            "phone": self.phone,
            "address": self.address
            # "favorites": [favorite.serialize() for favorite in self.favorites]
            # do not serialize the password, its a security breach
        }

class Vital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vital_name = db.Column(db.String(200), unique=False, nullable=False)	
    date = db.Column(db.String(200), unique=False, nullable=False)	
    value = db.Column(db.String(200), unique=False, nullable=False)		
    username = db.Column(db.String(20), db.ForeignKey('user.username'))

# { date: "2021-07-31", id: 0, value: 65.25, vitalName: "Heart Rate" },

    def __repr__(self):
        return '<Vital %r,%r,%r,%r,%r>' % (self.id, self.vital_name, self.date, self.value, self.username)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "vitalName": self.vital_name,
            "date": self.date,
            "value": self.value
            # do not serialize the password, its a security breach
        }

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=False, nullable=False)	
    dose = db.Column(db.String(120), unique=False, nullable=False)	
    frequency = db.Column(db.String(120), unique=False, nullable=False)		
    reason = db.Column(db.String(120), unique=False, nullable=False)	
    side_effects = db.Column(db.String(120), unique=False, nullable=False)	
    # username = db.Column(db.String(20), db.ForeignKey('user.username'))

# {	id: 1357,	name: "Aspirin",	dose: "a lot",  frequency: "too often", reason: "for fun", sideEffects: "madness and death" },

    def __repr__(self):
        return '<Medication %r,%r,%r,%r,%r,%r,%r>' % (self.id, self.username, self.name, self.dose, self.frequency, self.reason, self.side_effects)

    def serialize(self):
        return {
            "id": self.id,
            # "username": self.username,
            "name": self.name,
            "dose": self.dose,
            "frequency": self.frequency,
            "reason": self.reason,
            "side_effects": self.side_effects
        }

class Symptom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symptomName = db.Column(db.String(120), unique=False, nullable=False)	
    startDate = db.Column(db.String(200), unique=False, nullable=False)	
    severity = db.Column(db.Integer, unique=False, nullable=True)		
    location = db.Column(db.String(60), unique=False, nullable=True)	
    frequency = db.Column(db.String(120), unique=False, nullable=True)	
    symptom_note = db.relationship('SymptomNote', backref='symptom')
    duration = db.Column(db.String(120), unique=False, nullable=True)
    # vitals = db.relationship('Vital', backref='user')
    username = db.Column(db.String(20), db.ForeignKey('user.username'))

# { id: 123124, symptomName: "broken butt", startDate: "07/12/21", severity: "10", location: "butt", frequency: "constant", duration: "all day", notes: [] }


    def __repr__(self):
        return '<Symptom %r,%r,%r,%r,%r,%r,%r,%r,%r>' % (self.id, self.symptomName, self.startDate, self.startDate,self.severity, self.location, self.frequency, self.symptom_note, self.username)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "symptomName": self.symptomName,
            "startDate": self.startDate,
            "severity": self.severity,
            "location": self.location,
            "frequency": self.frequency,
            "duration": self.duration,
            "notes": [note.serialize() for note in self.symptom_note]
        }


class SymptomNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(200), unique=False, nullable=False)	
    severity = db.Column(db.Integer, unique=False, nullable=True)		
    symptom_id = db.Column(db.Integer, db.ForeignKey('symptom.id'))
    note = db.Column(db.String(500), unique=False, nullable=True)	


    def __repr__(self):
        return '<SymptomNote %r,%r,%r,%r,%r>' % (self.id, self.severity, self.date, self.symptom_id, self.note)

    def serialize(self):
        return {
            "id": self.id,
            "date": self.date,
            "symptom_id": self.symptom_id,
            "severity": self.severity,
            "description": self.note
        }

class AllDoctors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)	
    specialty = db.Column(db.String(200), unique=False, nullable=False)	


    def __repr__(self):
        return '<AllDoctors %r,%r,%r>' % (self.id, self.name, self.specialty)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "specialty": self.specialty
        }


# class NextVisit(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     symptomName = 
#     symptoms = 
#     meds = 
#     vitals = 

				# 	symptoms: [
				# 		{
				# 			id: 123124,
				# 			symptomName: "broken butt",
				# 			startDate: "07/12/21",
				# 			severity: "10",
				# 			location: "butt",
				# 			frequency: "constant",
				# 			duration: "all day",
				# 			notes: [{ date: "08/02/2021", description: "Getting better" }]
				# 		}
				# 	],
				# 	meds: [],
				# 	vitals: []
				# }

# id: store.allVisits.length, doctor: doctorName, date: date, time: time, symptoms: sympList, meds: medList, vitals: vitalList

    # def __repr__(self):
    #     return '<Favorite %r,%r,%r,%r,%r,%r,%r,%r>' % (self.id, self.date, self.time, self.doctorName,self.symptoms, self.meds, self.vitals, self.username)

    # def serialize(self):
    #     return {
    #         "id": self.id,
    #         "date": self.date,
    #         "time": self.time,
    #         "doctorName": self.doctorName,
    #         "symptoms": self.symptoms,
    #         "meds": self.meds,
    #         "vitals": self.vitals,
    #         "username": self.username
    #     }

