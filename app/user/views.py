from werkzeug.urls import url_parse

from flask import Blueprint, flash, redirect, url_for, render_template, request
from flask_login import current_user, login_required, login_user, logout_user

from app.db import db
from app.product.models import Snowboard
from app.user.models import User
from app.user.forms import RegistrationForm, LoginForm


blueprint = Blueprint('user', __name__, url_prefix='/user')


@blueprint.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('product.index'))
    title = 'Регистрация'
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password_hash(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Вы успешно зарегистрировались')
        return redirect(url_for('user.login'))
    return render_template('user/registration.html', page_title=title, form=form)


@blueprint.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('product.index'))
    title = 'Вход в личный кабинет'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('product.index')
        flash('Вы вошли на сайт')
        return redirect(next_page)
    return render_template('user/login.html', page_title=title, form=form)


@blueprint.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('Вы вышли из профиля')
    return redirect(url_for('product.index'))


@blueprint.route('/profile')
@login_required
def profile():
    title = 'Мои объявления'
    snowboards = Snowboard.query.filter(
        Snowboard.user_id == current_user.id, Snowboard.hidden != True
    ).order_by(Snowboard.ad_placement_date.desc()).all()
    return render_template('user/profile.html', page_title=title, snowboards=snowboards)


@blueprint.route('/hidden_ads')
@login_required
def hidden_ads():
    title = 'Скрытые объявления'
    snowboards = Snowboard.query.filter(
        Snowboard.user_id == current_user.id, Snowboard.hidden == True
    ).order_by(Snowboard.ad_placement_date.desc()).all()
    return render_template('user/hidden_ads.html', page_title=title, snowboards=snowboards)


@blueprint.route('/hide_ad/<int:snowboard_id>/')
@login_required
def hide_ad(snowboard_id):
    snowboard = Snowboard.query.get(snowboard_id)
    snowboard.hidden = True
    db.session.commit()
    flash('Вы скрыли объявление')
    return redirect(url_for('user.profile'))


@blueprint.route('/show_ad/<int:snowboard_id>/')
@login_required
def show_ad(snowboard_id):
    snowboard = Snowboard.query.get(snowboard_id)
    snowboard.hidden = False
    db.session.commit()
    flash('Вы убрали объявление из скрытых')
    return redirect(url_for('user.profile'))
