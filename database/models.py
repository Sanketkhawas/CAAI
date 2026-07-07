from database.database import db
from datetime import datetime


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    phone = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_verified = db.Column(db.Boolean, default=False)

    last_login = db.Column(db.DateTime)

    role = db.Column(db.String(20), default="user")

    documents = db.relationship('Document', backref='user')

    transactions = db.relationship('Transaction', backref='user')

    deductions = db.relationship('Deduction', backref='user')

    recommendations = db.relationship('Recommendation', backref='user')

    predictions = db.relationship('Prediction', backref='user')

    chat_history = db.relationship('ChatHistory', backref='user')

    investments = db.relationship('Investment', backref='user')

    tax_calculations = db.relationship('TaxCalculation', backref='user')


class Document(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    document_type = db.Column(db.String(100))

    file_name = db.Column(db.String(200))

    file_path = db.Column(db.String(300))

    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    ocr_status = db.Column(db.String(30))

    ocr_text = db.Column(db.Text)

    processed = db.Column(db.Boolean, default=False)


class Transaction(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    description = db.Column(db.String(200))

    amount = db.Column(db.Float)

    date = db.Column(db.String(50))

    category = db.Column(db.String(100))

    transaction_type = db.Column(db.String(20))

    merchant = db.Column(db.String(150))

    source = db.Column(db.String(50))


class Deduction(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    section = db.Column(db.String(50))

    amount = db.Column(db.Float)

    status = db.Column(db.String(50))

    proof_document = db.Column(db.String(300))

    financial_year = db.Column(db.String(20))

    remarks = db.Column(db.String(300))


class Recommendation(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    recommendation = db.Column(db.String(300))

    reason = db.Column(db.String(500))

    confidence_score = db.Column(db.Float)

    generated_by = db.Column(db.String(100))

    created_for_year = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Prediction(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    year = db.Column(db.Integer)

    predicted_tax = db.Column(db.Float)

    model_name = db.Column(db.String(100))

    confidence = db.Column(db.Float)

    actual_tax = db.Column(db.Float)


class ChatHistory(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    question = db.Column(db.String(500))

    answer = db.Column(db.String(1000))

    response_time = db.Column(db.Float)

    feedback = db.Column(db.String(100))

    source_document = db.Column(db.String(300))

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Investment(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    investment_type = db.Column(db.String(100))

    amount = db.Column(db.Float)

    section = db.Column(db.String(50))

    financial_year = db.Column(db.String(20))

    proof_document = db.Column(db.String(300))


class TaxCalculation(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    old_regime_tax = db.Column(db.Float)

    new_regime_tax = db.Column(db.Float)

    recommended_regime = db.Column(db.String(50))

    tax_saved = db.Column(db.Float)

    calculated_on = db.Column(db.DateTime, default=datetime.utcnow)


class OCRData(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    document_id = db.Column(db.Integer, db.ForeignKey('document.id'))

    raw_text = db.Column(db.Text)

    clean_text = db.Column(db.Text)

    entities = db.Column(db.Text)

    confidence = db.Column(db.Float)