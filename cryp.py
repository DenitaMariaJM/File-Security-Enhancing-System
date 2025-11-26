import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
backend = default_backend()
salt = b'\xe7\xd8O\xc2\x03\x13\xad5\xb9\x07\xe4]\xa94A\x1c'

def enc(file,key):
    try:
        print(file)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=backend
        )
        key = base64.urlsafe_b64encode(kdf.derive(key.encode()))
        f = Fernet(key)
        file = file.replace("/","\\")
        out_file = file.split("\\")
        out_file[-1] = "encrypted_"+out_file[-1]
        out_file = "\\".join(out_file)
        print(out_file)
        with open(file,"rb") as fl:
            cont = fl.read()
            with open(out_file,"wb") as f2:
                f2.write(f.encrypt(cont))
        return 1
    except:
        return 0

def dec(file,key):
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=backend
        )
        key = base64.urlsafe_b64encode(kdf.derive(key.encode()))
        f = Fernet(key)
        file = file.replace("/","\\")
        out_file = file.split("\\")
        out_file[-1] = "_".join(out_file[-1].split("_")[1:])
        out_file = "\\".join(out_file)
        print(out_file)
        with open(file,"rb") as fl:
            cont = fl.read()
            with open(out_file,"wb") as f2:
                f2.write(f.decrypt(cont))
        return 1
    except:
        return 0
