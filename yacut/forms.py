from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, SubmitField
from wtforms.validators import (DataRequired,
                                Length,
                                Optional,
                                URL,
                                ValidationError,
                                Regexp)

from .constants import MAX_SHORT_LENGTH, RESERVED


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
            Length(
                max=MAX_SHORT_LENGTH,
                message=f'Максимум {MAX_SHORT_LENGTH} символов.'
            ),
            Regexp(
                r'^[a-zA-Z0-9]+$',
                message=(
                    'Недопустимые символы. '
                    'Разрешены только латинские буквы и цифры.'
                ),),
        ],
    )
    submit = SubmitField('Создать')

    def validate_custom_id(self, field):
        if not field.data:
            return
        if field.data in RESERVED:
            raise ValidationError(
                'Предложенный вариант короткой ссылки уже существует.')


class FilesForm(FlaskForm):
    files = MultipleFileField(
        'Файлы',
        validators=[DataRequired(message='Обязательное поле.')],
    )
    submit = SubmitField('Загрузить')
