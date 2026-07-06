from flask import Flask
from database.database import db
from database.models import User

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():

    db.create_all()

@app.route('/')
def home():
    return "AI Tax Advisor Database Running"

if __name__ == "__main__":
    app.run(debug=True)