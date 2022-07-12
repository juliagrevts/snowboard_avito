from app import create_app
from app.product.parsers import save_product


app = create_app()
with app.app_context():
    save_product()
