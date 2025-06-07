import os
import json
import base64
from typing import Optional
from cryptography.fernet import Fernet

CRED_FILE = os.path.join(os.path.dirname(__file__), '..', 'credentials.enc')


def _fernet(master_password: str) -> Fernet:
    key = base64.urlsafe_b64encode(master_password.encode('utf-8').ljust(32, b'0'))
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
