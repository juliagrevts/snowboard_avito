from flask import Blueprint, render_template


blueprint = Blueprint('product', __name__)


@blueprint.route('/')
def index():
    title = 'Snowboard Shop'
    return render_template('product/index.html', page_title=title)
