import os
import datetime
import time

from mongoengine import connect, Q

from .models import User
from .auth import hasher

# mlab server
MONGO_USER = os.environ['MONGO_USER']
MONGO_KEY = os.environ['MONGO_KEY']
MONGO_DB = "linkous-prod"

MONGO_URI = "mongodb+srv://{}:{}@cluster0.jdsfj.mongodb.net/{}?retryWrites=true&w=majority".format(MONGO_USER, MONGO_KEY, MONGO_DB)

connect('linkous-prod', host=MONGO_URI)

def registerUser(user):
    """
    Accepts:
        user: {
            name,
            email,
            password,
            role
        }
    Returns:
        std-res
    """

    user_count = User.objects(email=user['email']).count()

    if user_count > 0:
        # User exists
        return {
            "status": "fail",
            "message": "email-exists"
        }

    if 'role' in user:
        # if user role is provided, set it
        user = User(
            name = user['name'],
            email = user['email'],
            password = hasher(user['password']),
            role = user['role']
        )

        if user['role'] == 'org':
            print('Creating API key for org: {}'. format(user['name']))
            api_key = hasher(user['email'] + str(time.time()))       

    else:
        # else, leave it default, which is 'user'
        user = User(
            name = user['name'],
            email = user['email'],
            password = hasher(user['password']),
        )
    
    # save into db
    process = user.save()
    
    res = {
        "status": "success",
        "message": "user-registered-with-id:{}".format(process.id)
        # "message": "user-registered-with-id:{}".format(1)
    }

    if user['role'] == 'org':
        API(
            user = user,
            api_key = api_key
        ).save()
        res['apiKey'] = api_key

    return res


# print(registerUser({
#     'name': 'Vaibhav',
#     'email': 'vaibhavkshinde20@gmail.com',
#     'password': 'root',
#     'role': 'admin'
# }))
