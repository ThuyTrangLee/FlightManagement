from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import logout_user, current_user
from flask_admin import Admin
from flight_management import app, db, model
from flask import redirect, url_for, current_app, session
from flask_admin import BaseView
from flask_login import current_user, logout_user


# Đăng xuất
class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == model.UserRole.ADMIN

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/login')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == model.UserRole.ADMIN

# Thống kê
# class StatView(BaseView):
#     @expose('/')
#     def index(self):
#         return self.render('admin/stats.html')

# def is_accessible(self):
#     return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN
class MybaseView(ModelView):
    # kiểm tra truy cập. Nếu đúng admin thì mới hiện lên
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == model.UserRole.ADMIN

class RoutesView(MybaseView):
    column_list = ['id', 'name', 'flights']
    can_export = True
    column_default_sort = ('id', True)
    column_sortable_list = ['id', 'name']
    column_searchable_list = ['id', 'name']
    column_editable_list = ['name']
    column_filters = ['id', 'name']
    column_labels = {
        'id': 'ID',
        'name': 'Tên tuyến bay',
        'flights': 'Các chuyến bay'
    }
    form_excluded_columns = ['airport', 'flights']

class FlightView(MybaseView):
    column_list = ['flight_name', 'routes','plane']
    # form_excluded_columns = ['tickets']
    can_export = True
    column_default_sort = ('id', True)
    column_sortable_list = ['id', 'flight_name']
    # column_searchable_list = ['id', 'flight_name', 'routes']
    column_editable_list = ['flight_name']
    column_filters = ['id', 'flight_name']
    column_labels = {
        'flight_name': 'Tên chuyến bay',
        'routes': 'Tuyến bay',
        'plane': 'Máy bay'
    }

admin = Admin(app, name='Quản lý chuyến bay')
admin.theme.fluid = True
admin.add_view(MybaseView(model.User, db.session, name="Tài khoản"))
admin.add_view(MybaseView(model.Profile, db.session, name='Thông tin'))
admin.add_view(MybaseView(model.FlightRoute, db.session, name='Tuyến bay'))
admin.add_view(MybaseView(model.Flight, db.session, name='Chuyến bay'))
admin.add_view(MybaseView(model.TicketClass, db.session, name='Hạng vé'))
admin.add_view(MybaseView(model.Seat, db.session, name='Ghế'))
admin.add_view(MybaseView(model.Setting, db.session, name='Quy định'))
admin.add_view(LogoutView(name='Đăng xuất'))
