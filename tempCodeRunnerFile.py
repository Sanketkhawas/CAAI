from routes.dashboard_routes import dashboard

app.register_blueprint(dashboard)
app = Flask(__name__)