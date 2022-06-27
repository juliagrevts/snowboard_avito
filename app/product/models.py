from app.db import db


class Snowboard(db.Model):
    __table_args__ = (
        db.UniqueConstraint('product_name', 'price', 'ad_text', 'user_id', 'url'), 
    )
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(128), nullable=False)
    ad_placement_date = db.Column(db.DateTime, nullable=False)
    address = db.Column(db.Text)
    price = db.Column(db.String(20), nullable=False)
    ad_text = db.Column(db.Text)
    user_id = db.Column(db.Integer)
    url = db.Column(db.String, nullable=True)
    photo_links = db.relationship('SnowboardPhotoLink', backref='snowboard')

    def __repr__(self):
        return f'<Snowboard {self.id} {self.product_name}>'


class SnowboardPhotoLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo_link = db.Column(db.String, unique=True)
    snowboard_id = db.Column(
        db.Integer,
        db.ForeignKey('snowboard.id', ondelete='CASCADE'),
        index=True
    )

    def __repr__(self):
        return f'<Snowboard photo {self.id} to snowboard {self.snowboard_id}>'
