from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate

from app.db import db
from app.product.views import blueprint as product_blueprint
from app.user.views import blueprint as user_blueprint
from app.user.models import User


def create_app(): 
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'

    app.register_blueprint(product_blueprint)
    app.register_blueprint(user_blueprint)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app
