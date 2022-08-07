from flask import abort, Blueprint, render_template

from app.product.models import Snowboard


blueprint = Blueprint('product', __name__)


@blueprint.route('/', defaults={'page': 1})
@blueprint.route('/<int:page>')
def index(page):
    title = 'КАТАЛОГ СНОУБОРДОВ'
    per_page = 15
    snowboards_pages_pagination = Snowboard.query.order_by(
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
    return render_template(
        'product/ad_page.html', page_title=snowboard.product_name, snowboard=snowboard
    )
