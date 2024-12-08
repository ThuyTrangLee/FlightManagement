from flight_management import db
import hashlib
from flight_management.model import User, Profile

def get_info_by_id(id):
    return Profile.query.filter(Profile.id == int(int)).first()

def load_user(user_id):
    return User.query.get(user_id)

def auth_user(username, password):
    password =str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    print(password)
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()