from flight_management import db
from flask_login import current_user
import hashlib
from flight_management import model

def get_info_by_id(user_id):
    return model.Profile.query.filter(model.Profile.id == int(user_id)).first()
    # return Profile.query.get(user_id)
def load_user(user_id):
    return model.User.query.get(user_id)

def auth_user(username, password):
    password =str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    print(password)
    return model.User.query.filter(model.User.username.__eq__(username.strip()),
                             model.User.password.__eq__(password)).first()

def get_info(identity=None, phone_number=None):

    return model.Profile.query.filter((model.Profile.cccd == identity) | (model.Profile.phone == phone_number)).first()

def add_user_info(name, phone_number, identity, email, commit=True):
    info = get_info(identity, phone_number)
    if info is None:
        info = model.Profile(name=name, phone=phone_number, email=email, cccd=identity)
        db.session.add(info)
        if commit:
            db.session.commit()
        return info
    else:
        return info

def get_acc(username):
    return db.session.query(model.User.username).filter(model.User.username.__eq__(username)).first()

def add_user(name, username, password, email, cccd, phone_number):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user_info = add_user_info(name, phone_number, cccd, email)
    u = model.User(id=user_info.id,username=username, password=password)
    db.session.add(u)
    db.session.commit()

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return model.User.query.filter(model.User.username.__eq__(username.strip()),
                                   model.User.password.__eq__(password)).first()
def add_flight_schedule(depart, depart_date_time, flight_duration, plane, ticket_class_data, im_airport):
    f = model.Flight( start_datetime=depart_date_time, flight_time=flight_duration,flight_route_id=depart, plane_id=plane,  staff_id=current_user.id)

    db.session.add(f)
    db.session.flush()

    for c in ticket_class_data:
        h = model.TicketClass(ticket_class_id=c['ticketClass'], quantity=c['quantity'], price=c['ticketPrice'],
                            flight_id=f.id)
        db.session.add(h)

    for s in im_airport:
        a = model.IntermAirport(airport_id=s['airportId'], flight_id=f.id, stop_time=s['duration'], note=s['note'])

        db.session.add(a)

    db.session.commit()

def load_plane():
    return model.Plane.query.all()
def load_airport():
    return model.Airport.query.all()