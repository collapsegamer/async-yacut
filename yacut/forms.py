from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, SubmitField
from wtforms.validators import (DataRequired,
                                Length,
                                Optional,
                                URL,
                                ValidationError
                                )

from .utils import RESERVED, is_short_valid


class URLMapForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле.'),
            URL(message='Некорректная ссылка.'),
        ],
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(max=16, message='Максимум 16 символов.'),
        ],
    )
    submit = SubmitField('Создать')

    def validate_custom_id(self, field):
        if not field.data:
            return
        if field.data in RESERVED:
            raise ValidationError(
                'Предложенный вариант короткой ссылки уже существует.')
        if not is_short_valid(field.data):
            raise ValidationError(
                'Недопустимые символы. '
                'Разрешены только латинские буквы и цифры.'
            )


class FilesForm(FlaskForm):
    files = MultipleFileField(
        'Файлы',
        validators=[DataRequired(message='Обязательное поле.')],
    )
    submit = SubmitField('Загрузить')
