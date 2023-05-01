from flask import Flask
from models import db
from flask_login import LoginManager
from routes.auth import auth_bp
from routes.views import views
from routes.user import user_bp
from routes.admin import admin_bp

app = Flask(__name__)

db.init_app(app)

with app.app_context():
    db.create_all()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///models/library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your-secret-key'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth_bp.login'

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

if __name__ == '__main__':
    app.run(debug=True)

