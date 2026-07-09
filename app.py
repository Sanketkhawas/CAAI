from flask import Flask
import os

from database.database import db
from database.models import User
from routes.auth_routes import auth

app = Flask(__name__)

# -----------------------------
# Application Configuration
# -----------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config['SECRET_KEY'] = 'CAAI-Development-Key-2026'

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(BASE_DIR, 'database', 'taxadvisor.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOAD_FOLDER'] = 'uploads/'

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB upload limit

# -----------------------------
# Initialize Database
# -----------------------------
db.init_app(app)

# -----------------------------
# Register Blueprints
# -----------------------------
app.register_blueprint(auth)

# -----------------------------
# Create Database Tables
# -----------------------------
with app.app_context():
    db.create_all()

# -----------------------------
# Home Route
# -----------------------------
@app.route('/')
def home():
    return "AI Tax Advisor Database Running"

# -----------------------------
# Run Application
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)