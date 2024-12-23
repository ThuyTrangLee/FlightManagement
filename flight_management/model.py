from sqlalchemy.testing.suite.test_reflection import users

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


class PayStatus(enum.Enum):
    UNPAID = 1  # chưa thanh toán
    UNCONFIRM = 2  # Hủy xác nhận
    PAID = 3  # đã thanh toán


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


class Profile(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    email = Column(String(50), unique=True)
    phone = Column(String(10), unique=True)
    cccd = Column(String(12), unique=True)


class User(Base, UserMixin):
    id = Column(Integer, ForeignKey(Profile.id), primary_key=True, nullable=False, unique=True)
    username = Column(String(50), unique=True)
    password = Column(String(50))
    user_role = Column(Enum(UserRole))
    profile = relationship("Profile", backref="user", lazy=True)

    def __str__(self):
        return f"{self.user_role.name} - {self.name}"

class Staff(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True, unique=True, nullable=False)
    user = relationship("User", backref="staff", lazy=True)
    flight_schedules = relationship("Flight", backref="staff", lazy=True)


class Customer(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True, unique=True, nullable=False)
    user = relationship("User", backref="customer", lazy=True)
    ticket = relationship("Ticket", backref="customer", lazy=True)


# sân bay
class Airport(Base):
    name = Column(String(50), nullable=False)
    address = Column(String(100), nullable=False)
    interm_airports = relationship('IntermAirport', backref=' interm_airports', lazy=True)  # san bay trung gian

    def __str__(self):
        return self.name


# Tuyến bay
class FlightRoute(Base):
    departure_id = Column(Integer, ForeignKey('airport.id'), nullable=False)  # đi
    arrival_id = Column(Integer, ForeignKey('airport.id'), nullable=False)  # dến
    departure = relationship('Airport', foreign_keys=[departure_id], backref='departure_route', lazy=True)
    arrival = relationship('Airport', foreign_keys=[arrival_id], backref='arrival_route', lazy=True)

    # chuyen_bay = relationship('ChuyenBay', backref='tuyen_bay', lazy=True)

    def __str__(self):
        return f"{self.departure} - {self.arrival}"


# SanBayTrungGian
class IntermAirport(Base):
    airport_id = Column(Integer, ForeignKey('airport.id'), nullable=False)
    flight_id = Column(Integer, ForeignKey('flight.id'), nullable=False)
    stop_time = Column(Integer, nullable=False)
    note = Column(String(100), nullable=True)
    __table_args__ = (
        UniqueConstraint('airport_id', 'flight_id'),
    )


# ghế
class Seat(Base):
    vertical= Column(Enum(IndexSeat), nullable=False)
    horizontal = Column(Integer, nullable=False)
    plane_seat = relationship('PlaneSeat', backref='seats', lazy=True)
    __table_args__ = (
        UniqueConstraint('vertical', 'horizontal'),
    )


# ghế máy bay
class PlaneSeat(Base):
    seat_id = Column(Integer, ForeignKey('seat.id'), nullable=False)
    plane_id = Column(Integer, ForeignKey('plane.id'), nullable=False)
    ticket = relationship('Ticket', backref='plane_seat', lazy=True)
    ticket_class_id = Column(Integer, ForeignKey('ticket_class.id'), nullable=False)
    __table_args__ = (
        UniqueConstraint('seat_id', 'plane_id'),
    )


# máy bay
class Plane(Base):
    name = Column(String(20), nullable=False)
    plane_seat = relationship('PlaneSeat', backref='plane', lazy=True)

    # chuyen_bay = relationship('ChuyenBay', backref='may_bay', lazy=True)

    def __str__(self):
        return self.name


# hạng vé
class TicketClass(Base):
    name = Column(String(20), nullable=False)
    flight_ticket_class = relationship('FlightTicketClass', backref='ticket_class', lazy=True)
    plane_seat = relationship('PlaneSeat', backref='ticket_class', lazy=True)

    def __str__(self):
        return self.name


# chuyến bay
class Flight(Base):
    start_datetime = Column(DateTime, nullable=True)
    flight_time = Column(Integer, nullable=False)

    flight_route_id = Column(Integer, ForeignKey('flight_route.id'), nullable=False)
    flight_route = relationship('FlightRoute', foreign_keys=[flight_route_id], lazy=True)

    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=True)

    plane_id = Column(Integer, ForeignKey('plane.id'), nullable=False)
    plane = relationship('Plane', foreign_keys=[plane_id], lazy=True)

    interm_airport = relationship('IntermAirport', backref='flight', lazy=True)


# HangVeChuyenBay
class FlightTicketClass(Base):
    ticket_class_id = Column(Integer, ForeignKey('ticket_class.id'), nullable=False)
    flight_id = Column(Integer, ForeignKey('flight.id'), nullable=False)
    quantity = Column(Integer, nullable=False)  # số lượng hạng vé này trên chuyến bay này
    price = Column(Integer, nullable=False)
    ticket = relationship('Ticket', backref='flight_ticket_class', lazy=True)
    __table_args__ = (
        UniqueConstraint('ticket_class_id', 'flight_id'),
    )


# vé
class Ticket(Base):
    plane_seat_id = Column(Integer, ForeignKey('plane_seat.id'), nullable=False)
    flight_ticket_class_id = Column(Integer, ForeignKey('flight_ticket_class.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    bill_id = Column(Integer, ForeignKey('bill.id'), nullable=True)
    __table_args__ = (
        UniqueConstraint('plane_seat_id', 'flight_ticket_class_id'),
    )


# hóa đơn
class Bill(Base):
    ticket = relationship('Ticket', backref='bill', uselist=False, lazy=True)
    create_date = Column(DateTime, nullable=False)
    status = Column(Enum(PayStatus), nullable=False, default=PayStatus.UNPAID)


class Setting(Base):
    key = Column(Enum(SettingKey), nullable=False, unique=True)
    value = Column(Integer, nullable=False)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # p1 = Profile(name="Thảo Trang",email="2251050074trang@ou.edu.vn", phone="0387975161", cccd="094304004797")
        # p2 = Profile(name="Trang Lee", email="2251050075trang@ou.edu.vn", phone="0327975181", cccd="054304010135")
        # p3 = Profile(name="Nguyễn Ngọc Thắng", email="thang@gmail.com", phone="0357975199", cccd="097304010135")
        # db.session.add_all([p1, p2, p3])
        # db.session.commit()
        # acc1 = User(id=p1.id, username="TrangThao", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
        #             user_role=UserRole.ADMIN)
        # acc2 = User(id=p2.id, username="TrangLee", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
        #             user_role=UserRole.STAFF)
        # acc3 = User(id=p3.id, username="Thang", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
        #             user_role=UserRole.CUSTOMER)
        # db.session.add_all([acc1, acc2, acc3])
        # db.session.commit()
        #
        # staff = Staff(id=2)
        # db.session.add(staff)
        # db.session.commit()
        #
        # customer = Customer(id=3)
        # db.session.add(customer)
        # db.session.commit()
        #
        # airport1 = Airport(name='Nội Bài', address='Hà Nội')
        # airport2 = Airport(name='Tân Sơn Nhất', address='TP Hồ Chí Minh')
        # airport3 = Airport(name='Cần Thơ', address='Cần Thơ')
        # airport4 = Airport(name='Đà Nẵng', address='Đà Nẵng')
        # airport5 = Airport(name='Cà Mau', address='Cà Mau')
        # airport6 = Airport(name='Phú Quốc', address='Phú Quốc')
        # airport7 = Airport(name='Điện Biên Phủ', address='Điện Biên')
        # airport8 = Airport(name='Thọ Xuân', address='Thanh Hóa')
        # airport9 = Airport(name='Phú Bài', address='Huế')
        # airport10 = Airport(name='Pleiku', address='Gia Lai')
        # airport11 = Airport(name='Chu Lai', address='Quảng Nam')
        # airport12 = Airport(name='Đồng Hới', address='Quảng Bình')
        # airport13 = Airport(name='Rạch Giá', address='Kiên Giang')
        # airport14 = Airport(name='Buôn Ma Thuột', address='Đắk Lắk')
        # airport15 = Airport(name='Liên Khương', address='Lâm Đồng')
        # airport16 = Airport(name='Côn Đảo', address='Bà Rịa - Vũng Tàu')
        # airport17 = Airport(name='Vinh', address='Nghệ An')
        # airport18 = Airport(name='Cam Ranh', address='Khánh Hòa')
        # airport19 = Airport(name='Tuy Hòa', address='Phú Yên')
        # airport20 = Airport(name='Phù Cát', address='Bình Định')
        # airport21 = Airport(name='Cát Bi', address='Hải Phòng')
        # airport22 = Airport(name='Vân Đồn', address='Quảng Ninh')
        # db.session.add_all([airport1, airport2, airport3, airport4, airport5, airport6, airport7, airport8, airport9, airport10, airport11, airport12, airport13, airport14, airport15, airport16, airport17, airport18, airport19, airport20, airport21, airport22])
        #
        # db.session.commit()
        # tb1 = FlightRoute(departure_id=1, arrival_id=2)  # Nội Bài -> Tân Sơn Nhất
        # tb2 = FlightRoute(departure_id=1, arrival_id=3)  # Nội Bài -> Cần Thơ
        # tb3 = FlightRoute(departure_id=2, arrival_id=4)  # Tân Sơn Nhất -> Đà Nẵng
        # tb4= FlightRoute(departure_id=3, arrival_id=5)  # Cần Thơ -> Cà Mau
        # tb5= FlightRoute(departure_id=4, arrival_id=6) # Đà Nẵng -> Phú Quốc
        # tb6= FlightRoute(departure_id=5, arrival_id=7) # Cà Mau -> Điện Biên Phủ
        # tb7= FlightRoute(departure_id=6, arrival_id=8)  # Phú Quốc -> Thọ Xuân
        # tb8= FlightRoute(departure_id=7, arrival_id=9)  # Điện Biên Phủ -> Phú Bài
        # tb9= FlightRoute(departure_id=8, arrival_id=10)  # Thọ Xuân -> Pleiku
        # tb10= FlightRoute(departure_id=9, arrival_id=11)  # Phú Bài -> Chu Lai
        # tb11= FlightRoute(departure_id=19, arrival_id=2)  # Tuy Hòa -> Tân sơn nhất
        # db.session.add_all([tb1, tb2, tb3, tb4 , tb5, tb6, tb7, tb8, tb9, tb10, tb11])
        # db.session.commit()
        #
        # # Tạo danh sách ghế và máy bay
        # plane1 = Plane(name='VietNam Airlines')
        # plane2 = Plane(name='Vietjet Air')
        # plane3 = Plane(name='Jetstar Pacific')
        # plane4 = Plane(name='Bamboo Airways')
        # list_seat = []
        # list_plane = [plane1, plane2, plane3, plane4]
        # # Số hàng và số cột
        # horizontal = 50 #hàng
        # vertical = ['A', 'B', 'C', 'D', 'E', 'F']
        #
        # # Tạo 300 ghế
        # for row in range(1, horizontal + 1):
        #     for column in vertical:
        #         seat = Seat(vertical=column, horizontal=row)
        #         list_seat.append(seat)
        #
        # # Lưu trữ ghế vào cơ sở dữ liệu
        # db.session.add_all(list_seat)
        # db.session.add_all(list_plane)
        # db.session.commit()
        #
        # hv1 = TicketClass(name='Thương Gia')
        # hv2 = TicketClass(name='Phổ Thông')
        # hv3 = TicketClass(name='Tiết Kiệm')
        #
        # db.session.add_all([hv1, hv2, hv3])
        # db.session.commit()
        #
        # # Thiết lập mối quan hệ giữa ghế và máy bay
        # for i in list_plane:
        #     for j in list_seat:
        #         # hạng thương gia
        #         if j.horizontal < 4:
        #             plane_seat = PlaneSeat(seat_id=j.id, plane_id=i.id, ticket_class_id=hv1.id)
        #             db.session.add(plane_seat)
        #         elif j.horizontal >= 4 and j.horizontal <= 30:
        #             # hạng tiết kiệm
        #             plane_seat = PlaneSeat(seat_id=j.id, plane_id=i.id, ticket_class_id=hv3.id)
        #             db.session.add(plane_seat)
        #         else:
        #             # hạng phổ thông
        #             plane_seat = PlaneSeat(seat_id=j.id, plane_id=i.id, ticket_class_id=hv2.id)
        #             db.session.add(plane_seat)
        # db.session.commit()
        #
        # qd1 = Setting(key=SettingKey.QUANAIRPORT, value=10)
        # qd2 = Setting(key=SettingKey.MINFLIGHT, value=30)
        # qd3 = Setting(key=SettingKey.MAXIMAIRPORT, value=3)
        # qd4 = Setting(key=SettingKey.MAXSTOP, value=30)
        # qd5 = Setting(key=SettingKey.MINSTOP, value=15)
        # qd6 = Setting(key=SettingKey.BASEPRICE, value=300000)
        # qd7 = Setting(key=SettingKey.BOOKINGTIME, value=720)
        # qd8 = Setting(key=SettingKey.SOLDTIME, value=240)
        # qd9 = Setting(key=SettingKey.NUTICKETCLASS, value=3)
        #
        # db.session.add_all([qd1, qd2, qd3, qd4, qd5, qd6, qd7, qd8, qd9])
        #
        # db.session.commit()
        #
