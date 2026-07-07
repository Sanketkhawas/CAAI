from flask import Flask
from database.database import db
from database.models import User
from routes.auth_routes import auth

app = Flask(__name__)

app.config['SECRET_KEY'] = 'CAAI-Development-Key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(auth)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return " AI Tax Advisor Database Running "

if __name__ == "__main__":
    app.run(debug=True)