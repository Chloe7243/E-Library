from flask import Flask
from routes.views import views
from auth.auth import auth

def start_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ete'

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app

run_app = start_app()
if __name__ == '__main__':
    run_app.run(debug=True)