import re

ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
SHORT_RE = re.compile(r'^[a-zA-Z0-9]{1,16}$')
RESERVED = {'admin', 'api', 'files'}

MAX_SHORT_LENGTH = 16