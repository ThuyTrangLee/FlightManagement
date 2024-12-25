from flight_management import db
from flask_login import current_user
import hashlib
from flight_management import model
from sqlalchemy import func
import cloudinary.uploader



def load_user(user_id):
    return model.User.query.get(user_id)

def auth_user(username, password):
    password =str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    print(password)
    return model.User.query.filter(model.User.username.__eq__(username.strip()),
                             model.User.password.__eq__(password)).first()

def add_user(name,phone,cccd,email,username,password,avatar=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = model.User(name=name.strip(),
                       username=username.strip(),
                       password=password,
                      cccd=cccd,
                      email=email,
                      phone=phone)
    if avatar:
        res = cloudinary.uploader.upload(avatar)
        user.avatar = res.get('secure_url')
    db.session.add(user)
    db.session.commit()




def add_flight_schedule(depart, depart_date_time, flight_duration, plane, ticket_class_data, im_airport):

    f = model.Flight( start_datetime=depart_date_time, flight_time=flight_duration,flight_route_id=depart, plane_id=plane,  staff_id=current_user.id)

    db.session.add(f)
    db.session.flush()

    for c in ticket_class_data:
        h = model.FlightTicketClass(ticket_class_id=c['ticketClass'], quantity=c['ticketPrice'], price=f.id,
                                    flight_id=f.id)
        db.session.add(h)

    for s in im_airport:
        a = model.IntermAirport(airport_id=s['airportId'], flight_id=f.id, stop_time=100, note=s['note'])

        db.session.add(a)

    db.session.commit()

def get_list_flight_in_search(fromm=None, to=None, departure=None):
    query = model.Flight.query

    if not fromm and not to and not departure:
        return query.limit(6).all()

    if fromm and int(fromm) > 0:
        query = query.filter(model.Flight.flight_route.has(
            model.FlightRoute.departure_id == int(fromm)
        ))

    if to and int(to) > 0:
        query = query.filter(model.Flight.flight_route.has(
            model.FlightRoute.arrival_id == int(to)
        ))

    if departure:
        query = query.filter(func.date(model.Flight.start_datetime) == departure)

    return query.order_by(model.Flight.start_datetime).all()