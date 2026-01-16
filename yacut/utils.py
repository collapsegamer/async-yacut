import random
import re

from .extensions import db
from .models import URLMap

ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
SHORT_RE = re.compile(r'^[a-zA-Z0-9]{1,16}$')

RESERVED = {'files'}


def is_short_valid(value: str) -> bool:
    if not value:
        return False
    return bool(SHORT_RE.fullmatch(value))


def get_unique_short_id() -> str:
    while True:
        short = ''.join(random.choice(ALPHABET) for _ in range(6))
        if short in RESERVED:
            continue
        exists = db.session.query(URLMap.id).filter_by(short=short).first()
        if not exists:
            return short
