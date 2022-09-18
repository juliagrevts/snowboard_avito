from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError


class SnowboardCreationForm(FlaskForm):
    product_name = StringField(
        'Название', 
        validators=[
            DataRequired(), Length(min=1, max=128, message='Должно содержать от 1 до 128 сивмолов')
        ],
        render_kw={'class': 'form-control'}
    )
    price = StringField(
        'Цена',
        validators=[
            DataRequired(), Length(min=1, max=20, message='Не может быть больше 20 знаков')
        ],
        render_kw={'class': 'form-control'}
    )
    address = StringField('Адрес', render_kw={'class': 'form-control'})
    ad_text = TextAreaField('Текст объявления', render_kw={'class': 'form-control'})
    phone_number = StringField(
        'Телефон',
        validators=[DataRequired(), Length(min=1, max=30, message='Не может быть больше 30 знаков')],
        render_kw={'class': 'form-control', 'placeholder':  '8 ___ ___-__-__'}
    )
    photos = MultipleFileField(
        'image',
        render_kw={'class': 'form-control'}
    )
    submit = SubmitField('Разместить объявление', render_kw={'class': 'btn btn-primary'})


    def validate_photos(self, photos):
        ALLOWED_EXTENSIONS = set(['jpg', 'pdf', 'png', 'jpeg', 'JPG'])
        file_storages = photos.data
        for f in file_storages:
            filename = f.filename
            if not (
                (filename == '') or
                ('.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS)
            ):
                raise ValidationError('Images only!')

