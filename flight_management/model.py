
from flight_management import app, db
import hashlib
import enum
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean, DateTime, Enum, Text, column, Interval, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, date, time

class UserRole(enum.Enum):
    STAFF = 1
    CUSTOMER = 2
    ADMIN = 3

# Vai trò của sân bay
class AirportRole(enum.Enum):
    DEPARTURE = 1
    ARRIVAL = 2
    INTERMEDIATE = 3  #sân bay trung gian

class IndexSeat(enum.Enum):
    A = 1
    B = 2
    C = 3

class Profile(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    email = Column(String(50), unique=True)
    birthday = Column(DateTime)
    gender = Column(Boolean)
    address = Column(Text)
    phone = Column(String(10), unique=True)
    cccd = Column(String(12), unique=True)

class User(db.Model):
    id = Column(Integer, ForeignKey(Profile.id), primary_key=True,nullable=False, unique=True)
    username = Column(String(50),unique=True)
    password = Column(String(50))
    avatar = Column(String(50))             #thêm defaulf vào
    user_role = Column(Enum(UserRole))
    profile = relationship('Profile', backref='user', lazy=True)

    def __str__(self):
        return f"{self.user_role.name} - {self.name}"

class Staff(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True, unique=True,nullable=False)
    user = relationship("User", backref="staff", lazy=True)
    flight_schedules = relationship("FlightSchedule", backref="staff", lazy=True)

class Customer(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True, unique=True, nullable=False)
    user = relationship("User", backref="customer", lazy=True)
    ticket = relationship("Ticket", backref="customer", lazy=True)

# sân bay
class Airport(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    airport_address = Column(String(50), nullable=False)

    def __str__(self):
        return self.name

# tuyến bay
class Routes(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    note = Column(String(500), nullable=True)
    airport = relationship("RoutesInfo", backref="routes")
    flight = relationship("Flight", backref="routes", lazy=True)
    def __str__(self):
        return self.name

# chi tiết tuyến bay
class RoutesInfo(db.Model):
    airport_id = Column(Integer, ForeignKey(Airport.id), primary_key=True)
    routes_id = Column(Integer, ForeignKey(Routes.id), primary_key=True)
    airport_role = Column(Enum(AirportRole), nullable=False)
    stop_time = Column(Float, nullable=True)
    note = Column(String(500), nullable=True)
# DONE

def default_value(column_name):
    def default(context):
        return context.get_current_parameters()[column_name]
    return default

# máy bay
class Plane(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    flight = relationship("Flight", backref="plane", lazy=True)

    def __str__(self):
        return self.name

# chuyến bay
class Flight(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    flight_name = Column(String(50), unique=True)
    plane_id = Column(Integer, ForeignKey(Plane.id), nullable=False)
    routes_id = Column(Integer, ForeignKey(Routes.id), nullable=False)
    flight_detail_id = relationship("FlightDetail", backref="flight", uselist=False)
    tickets = relationship("Ticket", backref="flight", lazy=True)

# lập lịch chuyên bay
class FlightSchedule(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    staff = Column(Integer, ForeignKey(Staff.id), nullable=False)
    flight_detail = relationship('FlightDetail', backref='flightSchedule', lazy=True)

# Chi tiết chuyến bay
class FlightDetail(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime, nullable=False)
    flight_duration = Column(Float, nullable=False)
    flight_id = Column(Integer, ForeignKey(Flight.id), nullable=False, unique=True)
    flight_schedule_id = Column(Integer, ForeignKey(FlightSchedule.id), nullable=False)
    num_of_seats_1st_class = Column(Integer, nullable=False)
    num_of_seats_2st_class = Column(Integer, nullable=False)
    num_of_empty_seats_1st_class = Column(Integer, default=default_value('num_of_seats_1st_class') ,nullable=False)
    num_of_empty_seats_2st_class = Column(Integer, default=default_value('num_of_seats_2st_class') ,nullable=False)

    def __str__(self):
        return f"Chi tiết chuyến bay có mã {self.flight_id}"
# hạng vé
class FareClass(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    seats = relationship("Seat", backref="fareClass", lazy=True)

    def __str__(self):
        return self.name

# ghế
class Seat(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    fare_class_id = Column(Integer, ForeignKey(FareClass.id), nullable=False)
    fare_class = relationship("FareClass", backref="seat", lazy=True)

    plane_id= Column(Integer, ForeignKey(Plane.id), nullable=False)
    plane = relationship("Plane", backref="seat", lazy=True)

    horizontal = Column(Enum(IndexSeat), nullable=False)
    vertical = Column(Integer, nullable=False)

    #ràng buộc dữ liệu số ghế là duy nhất
    __table_args__ =(
        UniqueConstraint('plane_id', 'horizontal','vertical', name='uni_plane_horizontal_vertical'),
        CheckConstraint(f'vertical >=1 AND vertical <= {app.config["VERTICAL_MAX"]}', name='Check_Vertical')
    )

    def __str__(self):
        return f"{self.plane} - {self.horizontal.name}{self.vertical} - {self.fare_class.name}"

# vé
class Ticket(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    booking_date = Column(DateTime, default=datetime.now())
    customer_id = Column(Integer, ForeignKey(User.id), nullable=False)
    customer = relationship("User", backref="take_tickets", lazy=True, foreign_keys=[customer_id])
    seat_id = Column(Integer, ForeignKey(Seat.id), nullable=False)
    flight_id = Column(Integer, ForeignKey(Flight.id), nullable=False)
    fare_class_id = Column(Integer, ForeignKey(FareClass.id), nullable=False)


class Settings(db.Model):
    id = Column(Integer, primary_key=True)
    thoi_gian_bay_toi_thieu = Column(Integer)
    so_san_bay_trung_gian_toi_da = Column(Integer)
    thoi_gian_dung_toi_thieu = Column(Integer)
    thoi_gian_dung_toi_da = Column(Integer)
    thoi_gian_ban_ve = Column(Integer)
    thoi_gian_dat_ve = Column(Integer)
    so_luong_hang_ve = Column(Integer)
    so_luong_san_bay= Column(Integer)
    thay_doi_don_gia_ve = Column(Integer)

    __table_args__ = (
        CheckConstraint('thoi_gian_bay_toi_thieu > 0', name='check_thoi_gian_bay_toi_thieu'),
        CheckConstraint('so_san_bay_trung_gian_toi_da > 0', name='check_so_san_bay_trung_gian_toi_da'),
        CheckConstraint('thoi_gian_dung_toi_thieu > 0', name='check_thoi_gian_dung_toi_thieu'),
        CheckConstraint('thoi_gian_dung_toi_da > 0', name='check_thoi_gian_dung_toi_da'),
        CheckConstraint('thoi_gian_ban_ve > 0', name='check_thoi_gian_ban_ve'),
        CheckConstraint('thoi_gian_dat_ve > 0', name='check_thoi_gian_dat_ve'),
        CheckConstraint('so_luong_hang_ve > 0', name='check_so_luong_hang_ve'),
        CheckConstraint('so_luong_san_bay> 0', name='check_so_luong_san_bay'),
        CheckConstraint('thay_doi_don_gia_ve >0', name='check_thay_doi_don_gia_ve')
    )

    def __str__(self):
        return f"Settings {self.id}"

if __name__== "__main__":
    with app.app_context():
        db.create_all()

        p1 = Profile(name="Thảo Trang")
        p2 = Profile(name="Trang Lee")
        p3 = Profile(name="Nguyễn Văn A")
        db.session.add_all([p1,p2,p3])
        db.session.commit()
        acc1 = User(id=p1.id, username="TrangThao", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()), user_role=UserRole.ADMIN)
        acc2 = User(id=p2.id, username="TrangLee", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),ser_role=UserRole.STAFF)
        acc3 = User(id=p3.id, username="user", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()), user_role=UserRole.CUSTOMER)
        db.session.add_all([acc1, acc2, acc3])
        db.session.commit()

        airport1 = Airport(name='Noi Bai', airport_address='Ha Noi')
        airport2 = Airport(name='Tan Son Nhat', airport_address='TP Ho Chi Minh')
        airport3 = Airport(name='Can Tho', airport_address='Can Tho')
        airport4 = Airport(name='Da Nang', airport_address='Da Nang')
        airport5 = Airport(name='Ca Mau', airport_address='Ca Mau')
        airport6 = Airport(name='Phu Quoc', airport_address='Phu Quoc')
        airport7 = Airport(name='Dien Bien Phu', airport_address='Dien Bien')
        airport8 = Airport(name='Tho Xuan', airport_address='Thanh Hoa')
        airport9 = Airport(name='Phu Bai', airport_address='Hue')
        airport10 = Airport(name='Pleiku', airport_address='Pleiku')
        airport11 = Airport(name='Chu Lai', airport_address='Chu Lai')
        airport12 = Airport(name='Dong Hoi', airport_address='Dong Hoi')
        airport13 = Airport(name='Rach Gia', airport_address='Rach Gia')
        airport14 = Airport(name='Buon Ma Thuot', airport_address='Buon Ma Thuot')
        airport15 = Airport(name='Lien Khuong', airport_address='Lien Khuong')
        airport16 = Airport(name='Con Dao', airport_address='Con Dao')
        airport17 = Airport(name='Vinh ', airport_address='Vinh ')

        db.session.add_all([airport1, airport2, airport3, airport4, airport5, airport6, airport7, airport8, airport9, airport10, airport11, airport12, airport13, airport14, airport15, airport16, airport17])
        db.session.commit()