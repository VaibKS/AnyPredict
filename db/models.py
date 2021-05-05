import datetime

from mongoengine import Document
from mongoengine import StringField, DateTimeField


class User(Document):
    meta = {"collection": "users"}
    name = StringField()
    email = StringField()
    password = StringField()
    role = StringField(default="user")
    joined_date = DateTimeField(default=datetime.datetime.utcnow)
