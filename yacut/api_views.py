from flask import Blueprint, jsonify, request

from .constants import MAX_SHORT_LENGTH
from .extensions import db
from .models import URLMap
from .utils import RESERVED, get_unique_short_id, is_short_valid

api_bp = Blueprint('api', __name__, url_prefix='/api')


def api_error(message: str, status: int):
    return jsonify({'message': message}), status


@api_bp.route('/id/', methods=['POST'], strict_slashes=False)
def create_short():
    data = request.get_json(silent=True)
    if data is None:
        return api_error('Отсутствует тело запроса', 400)

    url = data.get('url')
    if not url:
        return api_error('"url" является обязательным полем!', 400)

    custom_id = data.get('custom_id')
    if custom_id is not None:
        custom_id = str(custom_id)

    if custom_id:
        if (
            custom_id in RESERVED
            or len(custom_id) > MAX_SHORT_LENGTH
            or not is_short_valid(custom_id)
        ):
            return api_error(
                'Указано недопустимое имя для короткой ссылки',
                400,
            )

        if URLMap.query.filter_by(short=custom_id).first():
            return api_error(
                'Предложенный вариант короткой ссылки уже существует.',
                400,
            )

        short = custom_id
    else:
        short = get_unique_short_id()

    urlmap = URLMap(original=url, short=short)
    db.session.add(urlmap)
    db.session.commit()

    return jsonify(urlmap.to_api(request.host_url)), 201


@api_bp.route('/id/<string:short_id>/', methods=['GET'], strict_slashes=False)
def get_original(short_id: str):
    urlmap = URLMap.query.filter_by(short=short_id).first()
    if not urlmap:
        return api_error('Указанный id не найден', 404)
    return jsonify({'url': urlmap.original}), 200
