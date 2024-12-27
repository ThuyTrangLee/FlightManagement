from datetime import datetime, timedelta
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import logout_user, current_user
from flask_admin import Admin
from payos import PaymentData, ItemData
import time
from flight_management import app, db, model, dao, payos
from flask import redirect, url_for, current_app, session, render_template, request, flash
from flask_admin import BaseView
from flask_login import current_user, logout_user
from flight_management.model import SettingKey


class MybaseView(ModelView):
    column_default_sort = 'id'
    column_labels = {
        'active': 'Hoạt động',
        'created_date': 'Ngày tạo'
    }
    column_formatters = {
        'price': lambda v, c, m, p: f"{m.price:,.0f} VND"  # Định dạng số và thêm "VND"
    }

    # kiểm tra truy cập. Nếu đúng admin thì mới hiện lên
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == model.UserRole.ADMIN


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated and (
                    current_user.user_role == model.UserRole.ADMIN or current_user.user_role == model.UserRole.STAFF)

class PlaneView(MybaseView):
    column_labels = {
        **MybaseView.column_labels,
        'name': "Tên máy bay"
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


# # Tuyến bay
class FlightRouteVew(MybaseView):
    can_export = True
    column_default_sort = ('id', True)
    column_sortable_list = ['id']
    column_searchable_list = ['id']
    column_filters = ['id']
    column_labels = {
        **MybaseView.column_labels,
        'id': "ID",
        'departure': 'Sân bay đến',
        'arrival': 'Sân bay đi',
    }

class UserView(MybaseView):
    column_labels = {
        **MybaseView.column_labels,
        'name': 'Họ Tên',
        'phone': 'SĐT',
        'cccd': 'CCCD',
        'email':'Email',
        'username':'Tên đăng nhập',
        'password':'Mật khẩu',
        'avatar':'Avatar',
        'user_role':'Vai trò'
    }

class FlightView(MybaseView):
    can_export = True
    column_default_sort = ('id', True)
    column_sortable_list = ['id']
    column_searchable_list = ['id']
    column_filters = ['id']
    column_labels = {
        **MybaseView.column_labels,
        'flight_route': 'Tuyến bay',
        'staff': 'Nhân viên lập',
        'plane': 'Máy bay',
        'flight_time': 'Thời gian bay',
        'start_datetime': 'Ngày bay',
    }

class IntermAirportView(MybaseView):
    column_labels = {
        **MybaseView.column_labels,
        'airport': 'Sân bay',
        'flight_route': 'Tuyến bay',
        'stop_time': 'Thời gian dừng',
        'note': 'Ghi chú',
        'start_datetime': 'Ngày bay',
    }

class SeatView(MybaseView):
    column_labels = {
        **MybaseView.column_labels,
        'plane': 'Máy bay',
        'ticket_class': 'Hạng vé',
        'vertical': 'Vị trí cột',
        'horizontal': 'Vị trí hàng',
    }
class TicketView(MybaseView):
    column_labels = {
        **MybaseView.column_labels,
        'seat': 'Ghế',
        'flight': 'Chuyến bay',
        'customer': 'Khách hàng',
        'horizontal': 'Hàng',
        'name': 'Họ Tên',
        'phone': 'SĐT',
        'cccd': 'CCCD',
        'email': 'Email',
        'price': 'Giá vé'
    }

class TicketPriceView(MybaseView):
    column_labels = {
        **MybaseView.column_labels,
        'ticket_class': 'Hạng vé',
        'flight': 'Chuyến bay',
        'price': 'Giá vé'
    }

class TicketClassView(MybaseView):
    column_labels = {
        **MybaseView.column_labels,
        'name': 'Tên hạng'
    }

# chuyển thành tên để hiển thị
def format_enum_value(view, context, model, name):
    enum_value = getattr(model, name)
    if isinstance(enum_value, SettingKey):
        return enum_value.value  # Đổi thành enum_value.name nếu muốn hiển thị tên
    return enum_value


class SettingView(MybaseView):
    can_delete = False
    can_create = False
    column_editable_list = ['value']
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


class LapLichChuyenBayView(BaseView):
        @expose('/', methods=['GET', 'POST'])
        def index(self):
            settings = model.Setting.query.all()
            list_flight_route = model.FlightRoute.query.all()
            list_plane = model.Plane.query.all()
            list_airport = model.Airport.query.all()

            if request.method == "POST":
                flight_route_id = request.form.get('flight_route_id')
                flight_route = model.FlightRoute.query.filter(model.FlightRoute.id == int(flight_route_id)).first()

                list_airport_id = [flight_route.departure_id, flight_route.arrival_id]
                for i in range(settings[2].value):
                    airport_in = request.form.get(f'sanbaytrunggian-{i + 1}')
                    if airport_in and int(airport_in) > 0:
                        list_airport_id.append(int(airport_in))

                if len(list_airport_id) != len(set(list_airport_id)):
                    flash("Sân bay trung gian không hợp lệ", 'danger')
                    return redirect('/admin/laplichchuyenbayview/')

                plane_id = request.form.get('plane_id')
                start_datetime = request.form.get('start_date')
                flight_time = request.form.get('sum_flight_time')
                staff_id = current_user.id
                flight_id = dao.add_flight(staff_id=staff_id,
                                           flight_route_id=flight_route_id,
                                           plane_id=plane_id,
                                           start_datetime=start_datetime,
                                           flight_time=int(flight_time))

                for i in range(settings[2].value):
                    airport_in = request.form.get(f'sanbaytrunggian-{i + 1}')
                    stop_time = request.form.get(f'thoigiandung-{i + 1}')
                    note = request.form.get(f'ghichu-{i + 1}')
                    if airport_in and int(airport_in) > 0:
                        dao.add_airport_in(flight_route_id=flight_route_id, airport_id=int(airport_in), stop_time=stop_time,
                                           note=note)
                flash("Thêm thành công", 'success')
                return redirect('/admin/laplichchuyenbayview/')
            return self.render('admin/LapLichChuyenBay.html',
                               settings=settings,
                               list_flight_route=list_flight_route,
                               list_plane=list_plane,
                               list_airport=list_airport)

        def is_accessible(self):
            return current_user.is_authenticated and current_user.user_role == model.UserRole.STAFF


class BanVeView(BaseView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect('/admin')

        id = request.args.get('id', None)
        if not id:
            return redirect('/admin/tracuuview')

        flight = model.Flight.query.filter_by(id=id).first()
        seats = model.Seat.query.filter_by(plane_id=flight.plane_id).order_by('horizontal').all()
        vertical = 6
        horizontal = 6
        prices = model.TicketPrice.query.filter_by(flight_id=id).all()
        reversed_seats = model.ReservedSeat.query.filter_by(flight_id=id).all()
        reversed_seats_id = []
        for i in reversed_seats:
            reversed_seats_id.append(i.seat_id)

        is_con_han = True
        ngay_het_han = int((flight.start_datetime - timedelta(minutes=model.Setting.query.all()[7].value)).timestamp())
        if int(datetime.now().timestamp()) > ngay_het_han:
            is_con_han = False

        return self.render('admin/BanVe.html',
                           flight=flight,
                           seats=seats,
                           vertical=vertical,
                           horizontal=horizontal,
                           prices=prices,
                           flight_id=id,
                           reversed_seats_id=reversed_seats_id,
                           is_con_han=is_con_han)

    @expose('/create-payment-link', methods=["POST"])
    def create_payment_link(self):
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
                cancelUrl="http://127.0.0.1:5000/admin/banveview/cancel",
                returnUrl="http://127.0.0.1:5000/admin/banveview/success",
                expiredAt=orderCode + 600
            )
            payment_link_response = payos.createPaymentLink(payment_data)
        except Exception as e:
            return str(e)
        return redirect(payment_link_response.checkoutUrl)

    @expose('/success')
    def success(self):
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

                seat = model.ReservedSeat(seat_id=session.get('seat_selected_id'),
                                          flight_id=session.get('flight_id'))

            except Exception as e:
                return render_template(str(e))
            db.session.add(ticket)
            db.session.add(seat)
            db.session.commit()
        flash('Thanh toán thành công', 'success')
        return redirect('/admin/tracuuview')

    @expose('/cancel')
    def cancel(self):
        flash('Thanh toán thất bại', 'danger')
        return redirect('/admin/tracuuview')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == model.UserRole.STAFF


class TraCuuView(BaseView):
    @expose('/')
    def index(self):
        fromm = request.args.get('from', None)
        to = request.args.get('to', None)
        departure = request.args.get('departure', None)
        returnn = request.args.get('return', None)
        mode = request.args.get('mode', None)
        list_flight = dao.get_list_flight_in_search(fromm, to, departure)
        if mode:
                list_flight_2=dao.get_list_flight_in_search(to, fromm, returnn)
                list_flight= list(set(list_flight+list_flight_2))

        return self.render('admin/TraCuu.html', list_flight=list_flight)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == model.UserRole.STAFF
class LichSuBanVeView(BaseView):
    @expose('/')
    def index(self):
        list_payment = model.Ticket.query.filter_by(customer_id=current_user.id).order_by('created_date').all()

        return self.render('admin/LichSuBanVe.html',list_payment=list_payment)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == model.UserRole.STAFF

class ThongKeView(BaseView):
    @expose('/')
    def index(self):
        data = {}
        month = request.args.get('month')
        year = request.args.get('year')
        if month:
            max = 0
            list_flight_route = model.FlightRoute.query.order_by('id').all()
            total_price_all_flight_routes = 0
            for flight_route in list_flight_route:
                total_price_flight_route = 0
                count_flight = 0
                flag = False
                for flight in flight_route.flights:
                    for ticket in flight.tickets:
                        if ticket.created_date.month == int(month) and ticket.created_date.year == int(year):
                            total_price_flight_route += ticket.price
                            flag = True
                    if flag:
                        count_flight += 1
                if count_flight > max:
                    max = count_flight
                total_price_all_flight_routes += total_price_flight_route
                data[flight_route.getAddress()] = [total_price_flight_route, count_flight]

            for flight_route_name, values in data.items():
                total_price_flight_route = values[0]
                if total_price_all_flight_routes > 0:
                    percent = (total_price_flight_route / total_price_all_flight_routes) * 100
                else:
                    percent = 0
                values.append(percent)
            return self.render('admin/thongke.html',
                               labels=list(data.keys()),
                               month=month,
                               year=year,
                               data=[entry[0] for entry in data.values()],
                               percent=[entry[2] for entry in data.values()],
                               count=[entry[1] for entry in data.values()],
                               max=max)
        return self.render('admin/thongke.html')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == model.UserRole.ADMIN


# Trang của ADmin
admin = Admin(app, name='Quản lý chuyến bay')
admin.theme.fluid = True
admin.add_view(UserView(model.User, db.session, name="Tài khoản"))
admin.add_view(AiroportView(model.Airport, db.session, name="Sân bay"))
admin.add_view(FlightView(model.Flight, db.session, name="Chuyến bay"))
admin.add_view(FlightRouteVew(model.FlightRoute, db.session, name="Tuyến bay"))
admin.add_view(IntermAirportView(model.IntermAirport, db.session, name="Sân bay trung gian"))
admin.add_view(PlaneView(model.Plane, db.session, name="Máy bay"))
admin.add_view(SeatView(model.Seat, db.session, name="Ghế"))
admin.add_view(TicketView(model.Ticket, db.session, name="Vé"))
admin.add_view(TicketPriceView(model.TicketPrice, db.session, name="Danh sách đơn giá"))
admin.add_view(TicketClassView(model.TicketClass, db.session, name="Hạng vé"))
admin.add_view(SettingView(model.Setting, db.session, name="Quy định"))

admin.add_view(LapLichChuyenBayView(name="Lập lịch chuyến bay"))
admin.add_view(BanVeView(name="Bán Vé"))
admin.add_view(TraCuuView(name="Tra Cứu"))
admin.add_view(ThongKeView(name="Thống kê"))
admin.add_view(LichSuBanVeView(name="Lịch sử bán vé"))

admin.add_view(LogoutView(name="Đăng xuất"))
