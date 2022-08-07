from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from app.user.models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        'Имя пользователя',
        validators=[
            DataRequired(),
            Length(min=1, max=64, message='Имя пользователя должно содержать от 1 до 64 сивмолов')
        ],
        render_kw={'class': 'form-control'}
    )
    email = StringField(
        'Электронная почта',
        validators=[
            DataRequired(),
            Email(),
            Length(min=1, max=64, message='Адрес почты должен содержать от 1 до 64 сивмолов')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'name@example.com'}
    )
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={'class': 'form-control'})
    password2 = PasswordField(
        'Повторите пароль',
        validators=[DataRequired(), EqualTo('password', 'Пароли должны совпадать')],
        render_kw={'class': 'form-control'}
    )
    submit = SubmitField('Зарегистрироваться', render_kw={'class': 'btn btn-primary'})

    def validate_username(self, username):
        username_exists = User.query.filter_by(username=username.data).first()
        if username_exists:
            raise ValidationError('Пользователь с таким именем уже существует')
    
    def validate_email(self, email):
        email_exists = User.query.filter_by(email=email.data).first()
        if email_exists:
            raise ValidationError('Пользователь с таким почтовым адресом уже существует')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()], render_kw={'class': 'form-control'})
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={'class': 'form-control'})
    remember_me = BooleanField('Запомнить меня', default='checked', render_kw={'class': 'form-check-input'})
    submit = SubmitField('Войти', render_kw={'class': 'btn btn-primary'})

    def validate_username(self, username):
        username_exists = User.query.filter_by(username=username.data).first()
        if not username_exists:
            raise ValidationError('Неверное имя пользователя')
    
    def validate_password(self, password):
        user = User.query.filter_by(username=self.username.data).first()
        if user and not user.check_password_hash(password.data):
            raise ValidationError('Неверный пароль')