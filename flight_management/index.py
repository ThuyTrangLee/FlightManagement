from flight_management.decorators import role_only
from flask import render_template, redirect, url_for, request, flash
from flight_management import login, app
import dao
from flight_management.model import UserRole
from flight_management import model
from flask_login import LoginManager, login_required, current_user, login_user, logout_user


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
        flash("Tài khoản hoặc mật khẩu không đúng",'danger')
        return redirect(url_for('login_process'))
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

if __name__ == "__main__":
    from admin import *
    app.run(host='0.0.0.0', port=5000, debug=True)