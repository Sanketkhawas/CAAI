from flask import Flask
from database.database import db
<<<<<<< HEAD
from database.models import User
from routes.auth_routes import auth


app.config['SECRET_KEY'] = 'CAAI-Development-Key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
=======
from database.models import *
import os

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config['SECRET_KEY'] = 'your-secret-key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database', 'taxadvisor.db')

>>>>>>> 9b2f6a72c083866a12f229a13b9583e3d35fff31
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOAD_FOLDER'] = 'uploads/'

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db.init_app(app)

<<<<<<< HEAD
app.register_blueprint(auth)

=======
>>>>>>> 9b2f6a72c083866a12f229a13b9583e3d35fff31
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return " AI Tax Advisor Database Running "

if __name__ == "__main__":
    app.run(debug=True)