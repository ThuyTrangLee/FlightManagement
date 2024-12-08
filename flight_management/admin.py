from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import logout_user, current_user
from flask_admin import Admin
from flask import redirect, url_for, current_app
from flask_admin import BaseView
from model import *
from flask_login import current_user, logout_user

class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/login')

    def is_accessible(self):
        return current_user.is_authenticated


admin = Admin(app, name='=Quản lý chuyến bay',template_mode='bootstrap4' )