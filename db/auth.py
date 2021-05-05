import re
import hashlib
import os

# from flask import current_app as app
from flask import session
from .models import User

SALT = os.environ['SALT']

def hasher(s: str) -> str:
    return hashlib.sha256(str(s+SALT).encode()).hexdigest()

def signIn(email: str, password: str) -> bool:

    user = User.objects(email = email)

    if user.count() == 0:
        return False
    
    user = user[0]

    if hasher(password) == user['password']:
        # sign in success
        session['user'] = {
            "email": user['email'],
            "role": user['role']
        }
        return session['user']
    else:
        # sign in fail
        return False

def getUser():

    if not 'user' in session:
        return False
    
    user = User.objects.get(email=session['user']['email'])
    return user