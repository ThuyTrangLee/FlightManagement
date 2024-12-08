from flight_management.decorators import role_only
from flask import render_template, redirect, url_for, request
from flight_management import login, app
import dao
from flight_management.model import UserRole
from flask_login import login_required, current_user, login_user, logout_user

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.user_role == UserRole.ADMIN:
            return redirect("/admin")
        return redirect(url_for('home'))
    return redirect('login')

@app.route('/login', methods= ['GET','POST'])
def login_process():
    mse = ""
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user)
            return redirect("index")
        mse = "Tài khoản hoặc mật khẩu không đúng"
    return render_template('login.html', mse=mse)

@app.route("/log_out")
def logout():
    logout_user()
    return redirect(url_for("login"))

@login.user_loader
def user_load(user_id):
    return dao.get_info_by_id(user_id)

@app.route('/home')
@login_required
@role_only([UserRole.STAFF, UserRole.CUSTOMER])
def home():
    profile = dao.get_info_by_id(current_user.id)
    return render_template('index.html', profile=profile)

if __name__ == "__main__":
    with app.app_context():
        app.run(host='0.0.0.0', port=500,debug=True)