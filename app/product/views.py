from datetime import datetime
import io

from bson import Binary
from flask import (
    abort, Blueprint, flash, request, redirect, render_template, send_file, url_for 
)
from flask_login import current_user, login_required
from pymongo import MongoClient
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from app.db import db
from app.mongodb import collection
from app.product.forms import SnowboardCreationForm
from app.product.models import Snowboard


blueprint = Blueprint('product', __name__)


@blueprint.route('/', defaults={'page': 1})
@blueprint.route('/<int:page>')
def index(page):
    title = 'КАТАЛОГ СНОУБОРДОВ'
    per_page = 15
    snowboards_pages_pagination = Snowboard.query.filter(Snowboard.hidden != True).order_by(
        Snowboard.ad_placement_date.desc()
    ).paginate(page, per_page, False)
    return render_template(
        'product/index.html',
        page_title=title,
        snowboards_pages_pagination=snowboards_pages_pagination
    )


@blueprint.route('/snowboard/<int:snowboard_id>')
def ad_page(snowboard_id):
    snowboard = Snowboard.query.get(snowboard_id)
    if not snowboard:
        abort(404)
    mongo_photos_count = None
    if snowboard.mongodb_id:
        try:
            mongo_photos = collection.find_one({'snowboard_id': snowboard_id})['photos']
            mongo_photos_count = len(mongo_photos)
        except TypeError:
            mongo_photos_count = None
    return render_template(
        'product/ad_page.html',
        page_title=snowboard.product_name,
        snowboard=snowboard,
        photos_count=mongo_photos_count
    )


@blueprint.route('/ad_creation', methods=['GET', 'POST'])
@login_required
def create_ad():
    title = 'Новое объявление'
    try:
        form = SnowboardCreationForm()
        if form.validate_on_submit():

            snowboard_exists = Snowboard.query.filter(
                Snowboard.product_name == form.product_name.data,
                Snowboard.price == form.price.data,
                Snowboard.ad_text == form.ad_text.data,
                Snowboard.user_id == current_user.id
            ).count()
            if snowboard_exists:
                flash('У вас уже есть такое объявление')
                return redirect(url_for('product.create_ad'))
            new_snowboard = Snowboard(
                product_name=form.product_name.data,
                ad_placement_date=datetime.now(),
                address=form.address.data,
                price=form.price.data,
                ad_text=form.ad_text.data,
                phone_number=form.phone_number.data,
                user_id=current_user.id
            )
            db.session.add(new_snowboard)
            db.session.commit()

            file_storages = form.photos.data
            if not (len(file_storages) == 1 and file_storages[0].filename == ''):
                photos_list = []
                for f in file_storages:
                    filename = secure_filename(f.filename)
                    photo = Binary(f.read())
                    photo_tuple = (filename, photo)
                    photos_list.append(photo_tuple)
                mongodb_id = collection.insert_one(
                    {'snowboard_id': new_snowboard.id, 'photos': photos_list}
                ).inserted_id
                new_snowboard.mongodb_id = str(mongodb_id)
                db.session.add(new_snowboard)
                db.session.commit()
                
            flash('Вы разместили новое объявление')
            return redirect(url_for('user.profile'))
        
        return render_template(
            'product/ad_creation.html', page_title=title, form=form
        )

    except RequestEntityTooLarge:
        flash('Размер загружаемых файлов не должен быть больше 16 мб')
        return redirect(url_for('product.create_ad'))


@blueprint.route('/edit_ad/<int:snowboard_id>/', methods=['GET', 'POST'])
@login_required
def edit_ad(snowboard_id):
    title = 'Редактировать объявление'
    snowboard = Snowboard.query.get(snowboard_id)
    
    try:
        form = SnowboardCreationForm()
        if form.validate_on_submit():
            snowboard.product_name = form.product_name.data
            snowboard.ad_placement_date = datetime.now()
            snowboard.address = form.address.data
            snowboard.price = form.price.data
            snowboard.ad_text = form.ad_text.data
            snowboard.phone_number = form.phone_number.data

            file_storages = form.photos.data
            if not (len(file_storages) == 1 and file_storages[0].filename == ''):
                photos_list = []
                for f in file_storages:
                    filename = secure_filename(f.filename)
                    photo = Binary(f.read())
                    photo_tuple = (filename, photo)
                    photos_list.append(photo_tuple)
                    mongodb_id = collection.update_one(
                        {'snowboard_id': snowboard.id}, {'$set': {'photos': photos_list}},
                        upsert=True
                    ).upserted_id
                    snowboard.mongodb_id = str(mongodb_id)

            db.session.commit()

            flash('Вы отредактировали объявление')
            return redirect(url_for('user.profile'))
    
    except RequestEntityTooLarge:
        flash('Размер загружаемых файлов не должен быть больше 16 мб')
        return redirect(url_for('product.edit_ad', snowboard_id=snowboard.id))
    
    if request.method == 'GET':
        form.product_name.data = snowboard.product_name
        form.price.data = snowboard.price
        form.address.data = snowboard.address
        form.ad_text.data = snowboard.ad_text
        form.phone_number.data = snowboard.phone_number
        
    return render_template('product/ad_creation.html', page_title=title, form=form)


@blueprint.route('/snowboard_photo/<int:snowboard_id>/', defaults={'photo_index': None})
@blueprint.route('/snowboard_photo/<int:snowboard_id>/<int:photo_index>')
def render_image(snowboard_id, photo_index):
    try:
        snowboard_photos = collection.find_one({'snowboard_id': snowboard_id})['photos']
        if photo_index:
            photo_index = photo_index - 1
            snowboard_photo = io.BytesIO(snowboard_photos[photo_index][1])
            return send_file(
                snowboard_photo,
                download_name=snowboard_photos[photo_index][0]
            )
        first_snowboard_photo = io.BytesIO(snowboard_photos[0][1])
        return send_file(
            first_snowboard_photo,
            download_name=snowboard_photos[0][0]
        )
    except TypeError:
        return send_file(
            'static/no-photo.jpg' #add this image 'no-photo' to static
        )
