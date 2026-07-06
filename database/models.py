from database.database import db
from datetime import datetime

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    phone = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    documents = db.relationship('Document', backref='user')

    transactions = db.relationship('Transaction', backref='user')

    deductions = db.relationship('Deduction', backref='user')

    recommendations = db.relationship('Recommendation', backref='user')

    predictions = db.relationship('Prediction', backref='user')

    chat_history = db.relationship('ChatHistory', backref='user')

class Document(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    document_type = db.Column(db.String(100))

    file_name = db.Column(db.String(200))

    file_path = db.Column(db.String(300))

    upload_date = db.Column(db.DateTime, default=datetime.utcnow)


class Transaction(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    description = db.Column(db.String(200))

    amount = db.Column(db.Float)

    date = db.Column(db.String(50))

    category = db.Column(db.String(100))


class Deduction(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    section = db.Column(db.String(50))

    amount = db.Column(db.Float)

    status = db.Column(db.String(50))


class Recommendation(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    recommendation = db.Column(db.String(300))

    reason = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Prediction(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    year = db.Column(db.Integer)

    predicted_tax = db.Column(db.Float)


class ChatHistory(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    question = db.Column(db.String(500))

    answer = db.Column(db.String(1000))

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)