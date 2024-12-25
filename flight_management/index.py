from payos import ItemData, PaymentData

from flight_management.decorators import role_only
from flask import render_template, redirect, url_for, request, flash
from flight_management import login, app, payos
import dao
import json
from flight_management.model import UserRole
from flight_management import model
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
import time

@app.context_processor
def common_attributes():
    return {
        'ticketclass': model.TicketClass.query.all(),
        'plane': model.Plane.query.all(),
        'airport': model.Airport.query.all(),
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
    fromm = request.args.get('from', None)
    to = request.args.get('to', None)
    departure = request.args.get('departure', None)
    returnn = request.args.get('return', None)

    list_flight_1 = dao.get_list_flight_in_search(fromm,to,departure)
    list_flight_2 = []

    mode = 0
    if returnn:
        mode = 1
        list_flight_2 = dao.get_list_flight_in_search(to,fromm,returnn)
    list_flight = list(set(list_flight_1 + list_flight_2))
    return render_template("search.html",list_flight=list_flight, mode = mode)



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
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method.__eq__('POST'):
        name = request.form.get('name')
        phone = request.form.get('phone')
        cccd = request.form.get('cccd')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if model.User.query.filter_by(cccd=cccd).first():
            flash('CCCD đã được đăng ký', 'danger')
            return redirect('/register')

        if model.User.query.filter_by(phone=phone).first():
            flash('SĐT đã được đăng ký', 'danger')
            return redirect('/register')

        if model.User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã được đăng ký', 'danger')
            return redirect('/register')

        if not password.__eq__(confirm):
            flash('Mật khẩu không khớp!', 'danger')
            return redirect('/register')

        data = request.form.copy()
        del data['confirm']
        avatar = request.files.get('avatar')
        dao.add_user(avatar=avatar,
                     name=name,
                     phone=phone,
                     cccd=cccd,
                     email=email,
                     username=username,
                     password=password,
                     )

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
    return render_template('index.html')

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


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/discover')
def discover():
    return render_template('discover.html')

@app.route('/tickets_info/<int:id>')
def tickets_info(id):
    if not current_user.is_authenticated:
        return redirect('/login')

    flight = model.Flight.query.filter_by(id=id).first()
    seats = model.Seat.query.filter_by(plane_id=flight.plane_id).order_by('horizontal').all()
    vertical = 6
    horizontal = 6
    prices=model.TicketPrice.query.filter_by(flight_id=id).all()
    reversed_seats=model.ReservedSeat.query.filter_by(flight_id=id).all()
    reversed_seats_id = []
    for i in reversed_seats:
        reversed_seats_id.append(i.seat_id)
    return render_template('tickets_info.html',
                           flight=flight,
                           seats=seats,
                           vertical=vertical,
                           horizontal=horizontal,
                           prices=prices,
                           flight_id=id,
                           reversed_seats_id=reversed_seats_id)

@app.route('/cancel')
def cancel_payment():
    if current_user.is_authenticated:
        return render_template('cancel.html')
    return render_template('index.html')


@app.route('/success')
def success_payment():
    if current_user.is_authenticated:
        status = request.args.get('status')
        orderCode = request.args.get('orderCode')
        if status == 'PAID' and int(orderCode) == session.get('orderCode'):
            try:
                ticket = model.Ticket(seat_id=session.get('seat_selected_id'),
                                      flight_id=session.get('flight_id'),
                                      customer_id=current_user.id,
                                      name=session.get('name'),
                                      phone=session.get('phone'),
                                      cccd=session.get('cccd'),
                                      email=session.get('email'),
                                      price=session.get('seat_price'))

                seat= model.ReservedSeat(seat_id=session.get('seat_selected_id'),
                                         flight_id=session.get('flight_id'))

            except Exception as e:
                return render_template(str(e))
            db.session.add(ticket)
            db.session.add(seat)
            db.session.commit()

        return render_template('success.html')
    return render_template('index.html')

@app.route("/create-payment-link", methods=["POST"])
def create_payment_link():
    try:
        session['cccd'] = request.form.get('cccd')
        session['name'] = request.form.get('name')
        session['phone'] = request.form.get('phone')
        session['email'] = request.form.get('email')
        session['flight_id'] = request.form.get('flight_id')
        session['seat_selected_id'] = request.form.get('seat_selected_id')
        session['seat_price'] = request.form.get('seat_price')

        flight = model.Flight.query.filter_by(id=session['flight_id']).first()

        orderCode = int(time.time())
        session['orderCode'] = orderCode
        item = ItemData(name=f"{flight.flight_route}", quantity=1,
                        price=int(float(session['seat_price'])))
        payment_data = PaymentData(
            orderCode=orderCode,
            amount=int(float(session.get('seat_price'))),
            description="Mua vé máy bay",
            items=[item],
            cancelUrl="http://127.0.0.1:5000/cancel",
            returnUrl="http://127.0.0.1:5000/success",
            expiredAt=orderCode + 600
        )
        payment_link_response = payos.createPaymentLink(payment_data)
    except Exception as e:
        return str(e)
    return redirect(payment_link_response.checkoutUrl)

if __name__ == "__main__":
    from admin import *
    app.run(host='0.0.0.0', port=5000, debug=True)