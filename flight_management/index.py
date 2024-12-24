from flight_management.decorators import role_only
from flask import render_template, redirect, url_for, request, flash
from flight_management import login, app
import dao
import json
from flight_management.model import UserRole
from flight_management import model
from flask_login import LoginManager, login_required, current_user, login_user, logout_user


@app.context_processor
def common_attributes():
    return {
        'ticketclass': model.TicketClass.query.all(),
        'plane': dao.load_plane(),
        'airport': dao.load_airport(),
        'flight_route': model.FlightRoute.query.all(),
        'maxinairport': model.Setting.query.filter(model.Setting.key.__eq__(model.SettingKey.MAXIMAIRPORT)).first().value,
        'minstop': model.Setting.query.filter(model.Setting.key.__eq__(model.SettingKey.MINSTOP)).first().value,
        'nuticketclass': model.Setting.query.filter(model.Setting.key.__eq__(model.SettingKey.NUTICKETCLASS)).first().value,
    }

@login.user_loader
def user_load(user_id):
    return dao.load_user(user_id)

@app.route('/')
def index():
    # Kiểm tra quyền khi đăng nhập
    if current_user.is_authenticated:
        if current_user.user_role == UserRole.ADMIN:
            return redirect("/admin")
        return redirect(url_for('home'))
    return render_template("index.html")
@app.route('/search')
def search():
    return render_template("search.html")



@app.route('/login', methods=['GET', 'POST'])
def login_process():
    mse = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user)
            return redirect(url_for('index'))
        mse = "Tài khoản hoặc mật khẩu không đúng"
    return render_template('login.html', mse=mse)


@app.route('/register', methods=['POST', 'GET'])
def register_user():
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if not password.__eq__(confirm):
            flash('Mật khẩu không khớp!', 'danger')
            return redirect('/register')

        if dao.get_info(request.form.get('cccd'), request.form.get('phoneNumber')):
            flash('Tên CCCD hoặc SĐT đã được đăng ký', 'danger')
            return redirect('/register')

        if dao.get_acc(request.form.get('username')):
            flash('Tên đăng nhập đã được đăng ký', 'danger')
            return redirect('/register')

        if model.Profile.query.filter(model.Profile.email.__eq__(request.form.get('email'))).first():
            flash('Email đã được đăng ký', 'danger')
            return redirect('/register')

        dao.add_user(name=request.form.get('name'),
                     username=request.form.get('username'),
                     password=password,
                     email=request.form.get('email'),
                     cccd=request.form.get('cccd'),
                     phone_number=request.form.get('phoneNumber'),)
        flash('Đăng ký thành công!', 'success')
        return redirect('/register')

    return render_template('register.html')

@app.route("/log_out")
def logout():
    logout_user()
    return redirect(url_for("login_process"))

@app.route('/home')
@login_required
@role_only([UserRole.STAFF, UserRole.CUSTOMER])
def home():
    profile = dao.get_info_by_id(current_user.id)
    return render_template('index.html', profile=profile)

# Lập lịch chuyến bay
@app.route('/api/create_flight_schedule', methods=['POST'])
# @login_required
# @role_only([UserRole.STAFF])
def create_flight_schedule():
    if request.method.__eq__('POST'):
        depart = request.form.get('depart')
        plane = request.form.get('plane')
        depart_date_time = request.form.get('depart_date_time')
        flight_duration = request.form.get('flight_duration')
        tickets_data = json.loads(request.form.get('tickets_data'))
        im_airport = json.loads(request.form.get('im_airport'))

        try:
            dao.add_flight_schedule(depart, depart_date_time, flight_duration, plane, tickets_data, im_airport)
        except Exception as ex:
            print(ex)
            return redirect('/admin/')
        else:
            return redirect('/admin/')
if __name__ == "__main__":
    from admin import *
    app.run(host='0.0.0.0', port=5000, debug=True)