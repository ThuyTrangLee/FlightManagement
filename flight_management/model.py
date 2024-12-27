from flight_management import app, db
import hashlib
import enum
from flask_login import UserMixin
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean, DateTime, Enum, Text, column, Interval, \
    UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, date, time


class UserRole(enum.Enum):
    STAFF = 1
    CUSTOMER = 2
    ADMIN = 3


class IndexSeat(enum.Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'
    F = 'F'


class SettingKey(enum.Enum):
    QUANAIRPORT = "Số lượng sân bay"
    MINFLIGHT = "Thời gian bay tối thiểu"
    MAXIMAIRPORT = "Số lượng sân bay trung gian tối đa"
    MINSTOP = "Thời gian đừng tối thiểu"
    MAXSTOP = "Thời gian dừng tối đa"
    NUTICKETCLASS = "Số lượng hạng vé"
    BASEPRICE = "Đơn giá vé"
    SOLDTIME = "Thời gian bán vé"
    BOOKINGTIME = "Thời gian đặt vé"


# kế thừa lại lớp db.Model thêm 3 trường hạn chế lặp lại các trường khác, dữ liệu nhất quán
class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, autoincrement=True, primary_key=True)
    active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.now())


class User(Base, UserMixin):
    __tablename__= 'user'

    name = Column(String(50))
    phone = Column(String(10), unique=True)
    cccd = Column(String(12), unique=True)
    email = Column(String(50))
    username = Column(String(50), unique=True)
    password = Column(String(50))
    avatar = Column(String(100),
                    default="https://res.cloudinary.com/dcztds1is/image/upload/v1735012111/logo_kpzaej.jpg")
    user_role = Column(Enum(UserRole), default=UserRole.CUSTOMER)

    def __str__(self):
        return f"{self.user_role.name} - {self.name}"


# sân bay
class Airport(Base):
    __tablename__= 'airport'

    name = Column(String(50), nullable=False)
    address = Column(String(100), nullable=False)

    def __str__(self):
        return self.name


# Tuyến bay
class FlightRoute(Base):
    __tablename__= 'flight_route'

    departure_id = Column(Integer, ForeignKey('airport.id'), nullable=False)  # đi
    departure = relationship('Airport', backref='departure_route', lazy=True, foreign_keys=[departure_id])

    arrival_id = Column(Integer, ForeignKey('airport.id'), nullable=False)  # dến
    arrival = relationship('Airport', backref='arrival_route', lazy=True, foreign_keys=[arrival_id])

    def __str__(self):
        return f"{self.departure} - {self.arrival}"

    def getAddress(self):
        return f"{self.departure.address} - {self.arrival.address}"


# SanBayTrungGian
class IntermAirport(Base):
    __tablename__= 'interm_airport'

    airport_id = Column(Integer, ForeignKey('airport.id'), nullable=False)
    airport = relationship('Airport', backref='interm_airports', lazy=True, foreign_keys=[airport_id])

    flight_route_id = Column(Integer, ForeignKey('flight_route.id'), nullable=False)
    flight_route = relationship('FlightRoute', backref='interm_airports', lazy=True, foreign_keys=[flight_route_id])

    stop_time = Column(Integer, nullable=False)
    note = Column(String(100))

    __table_args__ = (
        UniqueConstraint('airport_id', 'flight_route_id'),
    )


# ghế
class Seat(Base):
    __tablename__= 'seat'

    vertical = Column(Enum(IndexSeat), nullable=False)
    horizontal = Column(Integer, nullable=False)

    plane_id = Column(Integer, ForeignKey('plane.id'), nullable=False)
    plane = relationship('Plane', backref='seats', lazy=True, foreign_keys=[plane_id])

    ticket_class_id = Column(Integer, ForeignKey('ticket_class.id'), nullable=False)
    ticket_class = relationship('TicketClass', backref='seats', lazy=True, foreign_keys=[ticket_class_id])

    __table_args__ = (
        UniqueConstraint('vertical', 'horizontal','plane_id'),
    )
    def __str__(self):
        return f"{self.vertical.value}{self.horizontal}"

# Ghe da dat
class ReservedSeat(Base):
    __tablename__ = 'reserved_seat'

    seat_id = Column(Integer, ForeignKey('seat.id'), nullable=False)
    seat = relationship('Seat', backref='reserved_seats', lazy=True)

    flight_id = Column(Integer, ForeignKey('flight.id'), nullable=False)
    flight = relationship('Flight', backref='reserved_seats', lazy=True)

    __table_args__ = (
        UniqueConstraint('seat_id', 'flight_id', name='uix_seat_flight'),
    )
# máy bay
class Plane(Base):
    __tablename__ = 'plane'

    name = Column(String(20), nullable=False)

    def __str__(self):
        return self.name

    def getSoLuongGheHang1(self):
        return  Seat.query.filter(Seat.plane_id == self.id, Seat.ticket_class_id==1).count()

    def getSoLuongGheHang2(self):
        return Seat.query.filter(Seat.plane_id == self.id, Seat.ticket_class_id==2).count()

# hạng vé
class TicketClass(Base):
    __tablename__ ='ticket_class'

    name = Column(String(20), nullable=False)

    def __str__(self):
        return self.name


# chuyến bay
class Flight(Base):
    __tablename__ = 'flight'

    flight_time = Column(Integer, nullable=False)
    start_datetime = Column(DateTime, nullable=True)

    flight_route_id = Column(Integer, ForeignKey('flight_route.id'), nullable=False)
    flight_route = relationship('FlightRoute', backref='flights', lazy=True, foreign_keys=[flight_route_id])

    staff_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    staff = relationship('User', backref='flights', lazy=True, foreign_keys=[staff_id])

    plane_id = Column(Integer, ForeignKey('plane.id'), nullable=False)
    plane = relationship('Plane', backref='flights', lazy=True, foreign_keys=[plane_id])

    def getHour(self):
        gio = self.flight_time // 60
        phut = self.flight_time % 60
        if gio == 0:
            return f"{phut} Phút"
        return f"{gio} Giờ {phut} Phút"

# danh sách đơn giá vé
class TicketPrice(Base):
    __tablename__ ='ticket_price'

    ticket_class_id = Column(Integer, ForeignKey('ticket_class.id'), nullable=False)
    ticket_class = relationship('TicketClass', backref='ticket_prices', lazy=True, foreign_keys=[ticket_class_id])

    flight_id = Column(Integer, ForeignKey('flight.id'), nullable=False)
    flight = relationship('Flight', backref='ticket_prices', lazy=True, foreign_keys=[flight_id])

    price = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('ticket_class_id', 'flight_id'),
    )
# vé
class Ticket(Base):
    __tablename__ ='ticket'

    seat_id = Column(Integer, ForeignKey('seat.id'), nullable=False)
    seat = relationship('Seat', backref='tickets', lazy=True, foreign_keys=[seat_id])

    flight_id = Column(Integer, ForeignKey('flight.id'), nullable=False)
    flight = relationship('Flight', backref='tickets', lazy=True, foreign_keys=[flight_id])

    customer_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    customer = relationship('User', backref='tickets', lazy=True, foreign_keys=[customer_id])

    name = Column(String(50))
    phone = Column(String(10))
    cccd = Column(String(12))
    email = Column(String(50))

    price = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint('seat_id', 'flight_id'),
    )

class Setting(Base):
    key = Column(Enum(SettingKey), nullable=False, unique=True)
    value = Column(Integer, nullable=False)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()


