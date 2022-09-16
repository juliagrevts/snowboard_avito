from crypt import methods
from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import current_user, login_user, logout_user

from app.db import db
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
        flash('Вы вошли на сайт')
        return redirect(url_for('product.index'))
    return render_template('user/login.html', page_title=title, form=form)


@blueprint.route('/logout')
def logout():
    logout_user()
    flash('Вы вышли из профиля')
    return redirect(url_for('product.index'))
