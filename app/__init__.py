from flask import Flask
from flask_migrate import Migrate

from app.db import db
from app.product.models import Snowboard, SnowboardPhotoLink
from app.product.views import blueprint as product_blueprint


def create_app(): 
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)
    migrate = Migrate(app, db)

    app.register_blueprint(product_blueprint)
    
    return app
