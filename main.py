from flask import Flask
from models import db, User
from flask_login import LoginManager, current_user
from routes.auth import auth_bp
from routes.views import views
from routes.user import user_bp
from routes.admin import admin_bp

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "your-secret-key"

db.init_app(app)

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@login_manager.request_loader
def load_user_from_request(request):
    # Check if the request contains a valid authentication token
    auth_token = request.headers.get("Authorization")
    if auth_token:
        # Verify the token and return the corresponding user object
        user = User.verify_auth_token(auth_token)
        if user:
            return user

    # If no valid authentication token was found, return None
    return None


# Inject global variables into all templates
@app.context_processor
def inject_global_vars():
    return dict(user=current_user)


app.register_blueprint(views)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

if __name__ == "__main__":
    app.run(debug=True)
