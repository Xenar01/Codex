import os
import json
import base64
import hashlib
from typing import Optional
from cryptography.fernet import Fernet

BASE_DIR = os.path.dirname(__file__)
CRED_FILE = os.path.join(BASE_DIR, '..', 'credentials.enc')
SALT_FILE = os.path.join(BASE_DIR, '..', 'credentials.salt')


def _fernet(master_password: str) -> Fernet:
    if not os.path.exists(SALT_FILE):
        with open(SALT_FILE, 'wb') as f:
            f.write(os.urandom(16))
    with open(SALT_FILE, 'rb') as f:
        salt = f.read()
    dk = hashlib.pbkdf2_hmac('sha256', master_password.encode('utf-8'), salt, 100000, dklen=32)
    key = base64.urlsafe_b64encode(dk)
    return Fernet(key)


def save_credentials(site: str, username: str, password: str, master_password: str) -> None:
    f = _fernet(master_password)
    data = {}
    if os.path.exists(CRED_FILE):
        with open(CRED_FILE, 'rb') as fh:
            decrypted = f.decrypt(fh.read())
            data = json.loads(decrypted.decode('utf-8'))
    data[site] = {'username': username, 'password': password}
    with open(CRED_FILE, 'wb') as fh:
        fh.write(f.encrypt(json.dumps(data).encode('utf-8')))


def load_credentials(site: str, master_password: str) -> Optional[dict]:
    if not os.path.exists(CRED_FILE):
        return None
    f = _fernet(master_password)
    with open(CRED_FILE, 'rb') as fh:
        decrypted = f.decrypt(fh.read())
        data = json.loads(decrypted.decode('utf-8'))
    return data.get(site)
