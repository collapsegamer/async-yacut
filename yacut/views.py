import asyncio
import uuid
from io import BytesIO

import aiohttp
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
)

from .extensions import db
from .forms import FilesForm, URLMapForm
from .models import URLMap
from .utils import RESERVED, get_unique_short_id, is_short_valid
from .ydisk import download_bytes, get_download_href, get_upload_href, upload_bytes

ui_bp = Blueprint('ui', __name__)


def _short_url(short: str) -> str:
    return request.host_url.rstrip('/') + '/' + short


@ui_bp.route('/', methods=['GET', 'POST'])
def index():
    form = URLMapForm()
    short_url = None

    if form.validate_on_submit():
        original = form.original_link.data
        custom = (form.custom_id.data or '').strip() or None

        if custom:
            if custom in RESERVED or (len(custom) > 16) or (not is_short_valid(custom)):
                flash('Предложенный вариант короткой ссылки уже существует.')
                return render_template('index.html', form=form, short_url=None)

            if URLMap.query.filter_by(short=custom).first():
                flash('Предложенный вариант короткой ссылки уже существует.')
                return render_template('index.html', form=form, short_url=None)

            short = custom
        else:
            short = get_unique_short_id()

        db.session.add(URLMap(original=original, short=short))
        db.session.commit()
        short_url = _short_url(short)

    return render_template('index.html', form=form, short_url=short_url)


@ui_bp.route('/files', methods=['GET', 'POST'])
def files():
    form = FilesForm()
    results = []

    if form.validate_on_submit():
        token = current_app.config.get('DISK_TOKEN')
        if not token:
            flash('Не настроен DISK_TOKEN.')
            return render_template('files.html', form=form, results=[])

        uploaded_files = form.files.data

        async def _upload_all():
            async with aiohttp.ClientSession() as session:
                async def _one(fs):
                    filename = fs.filename or 'file'
                    content = fs.read()

                    # Тест: path должен содержать '/' перед именем файла.
                    disk_path = f'app:/yacut/{uuid.uuid4().hex}/{filename}'

                    href = await get_upload_href(session, token, disk_path)
                    await upload_bytes(session, href, content)

                    # Тест: после upload должен быть вызван download endpoint.
                    await get_download_href(session, token, disk_path)

                    short = get_unique_short_id()
                    db.session.add(URLMap(original=f'ydisk:{disk_path}:{filename}', short=short))
                    return filename, short

                return await asyncio.gather(*(_one(f) for f in uploaded_files))

        try:
            pairs = asyncio.run(_upload_all())
            db.session.commit()
            results = [{'filename': fn, 'short_url': _short_url(short)} for fn, short in pairs]
        except Exception:
            db.session.rollback()
            flash('Ошибка загрузки файлов.')

    return render_template('files.html', form=form, results=results)


@ui_bp.route('/<string:short_id>')
def follow(short_id: str):
    if short_id in RESERVED:
        abort(404)

    urlmap = URLMap.query.filter_by(short=short_id).first()
    if not urlmap:
        abort(404)

    original = urlmap.original

    if not original.startswith('ydisk:'):
        return redirect(original)

    token = current_app.config.get('DISK_TOKEN')
    if not token:
        abort(500)

    _, rest = original.split('ydisk:', 1)
    if ":" not in rest:
        abort(500)
    disk_path, filename = rest.split(':', 1)

    async def _download():
        async with aiohttp.ClientSession() as session:
            href = await get_download_href(session, token, disk_path)
            return await download_bytes(session, href)

    try:
        data = asyncio.run(_download())
    except Exception:
        abort(500)

    return send_file(BytesIO(data), as_attachment=True, download_name=filename)
