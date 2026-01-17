import random

from .constants import RESERVED, ALPHABET, SHORT_RE
from .extensions import db
from .models import URLMap


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
