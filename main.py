from flask import Flask
from models import db
from routes.auth import auth_bp
from routes.views import views

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///models/library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your-secret-key'
app.register_blueprint(auth_bp)
app.register_blueprint(views)

db.init_app(app)


if __name__ == '__main__':
    app.run(debug=True)

