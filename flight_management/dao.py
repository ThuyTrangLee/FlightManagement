from flight_management import db
import hashlib
from flight_management.model import User, Profile, Airport
from flight_management import model

def get_info_by_id(user_id):
    return Profile.query.filter(Profile.id == int(user_id)).first()
    # return Profile.query.get(user_id)
def load_user(user_id):
    return User.query.get(user_id)

def auth_user(username, password):
    password =str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    print(password)
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()

def get_info(identity=None, phone_number=None):

    return model.Profile.query.filter((model.Profile.cccd == identity) | (model.Profile.phone == phone_number)).first()

def add_user_info(name, phone_number, identity, email, commit=True):
    info = get_info(identity, phone_number)
    if info is None:
        info = Profile(name=name, phone=phone_number, email=email, cccd=identity)
        db.session.add(info)
        if commit:
            db.session.commit()
        return info
    else:
        return info

def get_acc(username):
    return db.session.query(User.username).filter(User.username.__eq__(username)).first()

def add_user(name, username, password, email, cccd, phone_number):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user_info = add_user_info(name, phone_number, cccd, email)
    u = User(id=user_info.id,username=username, password=password)
    db.session.add(u)
    db.session.commit()

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()


# def get_depature_points():
#     return Airport.query.All()