from dotenv import load_dotenv
from flask import Flask
import os

from flask_login import LoginManager
from routes.chatbot_routes import chatbot
from database.database import db
from database.models import User
from routes.auth_routes import auth
from routes.dashboard_routes import dashboard
from routes.upload_routes import upload_bp
load_dotenv()
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
# Initialize Flask-Login
# -----------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'          # where @login_required redirects to
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -----------------------------
# Register Blueprints
# -----------------------------
app.register_blueprint(auth)
app.register_blueprint(dashboard)
app.register_blueprint(upload_bp)
app.register_blueprint(chatbot)

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
    return "AI Tax Advisor Running"

# -----------------------------
# Run Application
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)