from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import logout_user, current_user
from flask_admin import Admin
from flight_management import app, db, model
from flask import redirect, url_for, current_app, session
from flask_admin import BaseView
from flask_login import current_user, logout_user
from flight_management.model import *


class MybaseView(ModelView):
    column_default_sort = 'id'
    column_labels = {
        'active': 'Hoạt động',
        'created_date': 'Ngày tạo'
    }
    column_formatters = {
        'Price': lambda v, c, m, p: f"{m.Price:,.0f} VND"  # Định dạng số và thêm "VND"
    }

    # kiểm tra truy cập. Nếu đúng admin thì mới hiện lên
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == model.UserRole.ADMIN


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/login')

    def is_accessible(self):
        return current_user.is_authenticated


class UserView(MybaseView):
    column_labels = {
        'profile': 'ID',
        'username': 'Tên đăng nhập',
        'password': 'Mật khẩu'
    }


class AiroportView(MybaseView):
    column_list = ['id', 'name', 'address']
    column_searchable_list = ['name', 'address']
    column_filters = ['name', 'address']
    column_labels = {
        'id': 'ID',
        'name': 'Tên máy bay',
        'address': 'Tỉnh'
    }


# Tuyến bay
class FlightRouteVew(MybaseView):
    column_list = ['id', 'departure', 'arrival', 'departure.name']
    can_export = True
    column_default_sort = ('id', True)
    column_sortable_list = ['id']
    column_searchable_list = ['id', 'departure.name']
    column_labels = {
    'id': "ID",
    'departure': 'Sân bay đến',
    'arrival': 'Sân bay đi'
    }


# class RoutesView(MybaseView):
#     column_list = ['id', 'name', 'flights']
#     can_export = True
#     column_default_sort = ('id', True)
#     column_sortable_list = ['id', 'name']
#     column_searchable_list = ['id', 'name']
#     column_editable_list = ['name']
#     column_filters = ['id', 'name']
#     column_labels = {
#         'id': 'ID',
#         'name': 'Tên tuyến bay',
#         'flights': 'Các chuyến bay'
#     }
#     form_excluded_columns = ['airport', 'flights']

# chuyển thành tên để hiển thị
def format_enum_value(view, context, model, name):
    enum_value = getattr(model, name)
    if isinstance(enum_value, SettingKey):
        return enum_value.value  # Đổi thành enum_value.name nếu muốn hiển thị tên
    return enum_value


class SettingView(MybaseView):
    can_delete = False
    can_create = False
    column_list = ['key', 'value', 'created_date']

    column_formatters = {
        'key': format_enum_value
    }
    # form_excluded_columns = ['created_date', 'nhan_vien_quan_tri']
    column_labels = {
        'key': 'Tên Quy Định',
        'value': 'Giá Trị',
        'active': 'Hoạt Động',
        'created_date': 'Ngày Thay Đổi Gần Nhất',
    }

    def on_model_change(self, form, model, is_created):
        model.created_date = datetime.now()
        model.nhan_vien_quan_tri_id = current_user.id

class CustomScheduleView(MybaseView):
    @expose('/create_flight_schedule/', methods=('GET', 'POST'))
    # create_template = 'flight_schedule.html'
    def create_view(self):
        # flightroute = model.FlightRoute.query.all()
        # planes = model.Plane.query.all()
        # ticketclass = model.TicketClass.query.all()

        return self.render('flight_schedule.html')

    def is_accessible(self):
        return current_user.is_authenticated and (current_user.user_role == model.UserRole.STAFF or current_user.user_role == model.UserRole.ADMIN)

    column_labels = {
        'flight_route': 'Tuyến bay',
        'plane': 'Máy bay',
        'start_datetime': 'Ngày - giờ khởi hành',
        'flight_time': "Thời gian bay",
        'staff': 'Nhân viên lập'
    }

# Thống kê
# class StatView(BaseView):
#     @expose('/')
#     def index(self):
#         return self.render('admin/stats.html')

admin = Admin(app, name='Quản lý chuyến bay')
admin.theme.fluid = True
admin.add_view(UserView(model.User, db.session, name="Tài khoản"))
admin.add_view(MybaseView(model.Profile, db.session, name='Thông tin'))
admin.add_view(FlightRouteVew(model.FlightRoute, db.session, name='Tuyến bay'))
admin.add_view(AiroportView(model.Airport, db.session, name="Sân bay"))
admin.add_view(CustomScheduleView(model.Flight, db.session, name='Chuyến bay'))
admin.add_view(MybaseView(model.TicketClass, db.session, name='Hạng vé'))
admin.add_view(MybaseView(model.Ticket, db.session, name="Vé"))
admin.add_view(MybaseView(model.Seat, db.session, name='Ghế'))
admin.add_view(MybaseView(model.Bill, db.session, name="Giao Dich"))
admin.add_view(SettingView(model.Setting, db.session, name='Quy định'))
