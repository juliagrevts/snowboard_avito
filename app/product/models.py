from app.db import db


class Snowboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(128), nullable=False)
    ad_placement_date = db.Column(db.DateTime, nullable=False)
    address = db.Column(db.Text)
    price = db.Column(db.String(20), nullable=False)
    ad_text = db.Column(db.Text)

    def __repr__(self):
        return f'<Snowboard {self.id} {self.product_name}>'

