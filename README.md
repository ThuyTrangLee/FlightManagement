# ✈️ Flight Management System

Hệ thống **Quản lý chuyến bay** hỗ trợ đặt vé trực tuyến, bán vé tại quầy, lập lịch chuyến bay, thống kê doanh thu và quản trị quy định. Dự án được thực hiện trong phạm vi môn học *CÔng nghệ phần mềm*.

---

## 📌 Tính năng chính
- **Đặt vé trực tuyến**: tìm chuyến bay → chọn ghế → thanh toán online → nhận e-ticket qua email.
- **Tra cứu chuyến bay** theo tuyến bay, ngày đi/về.
- **Nhân viên bán vé** tại quầy (nhập thông tin khách, xác nhận thanh toán).
- **Lập lịch chuyến bay**: thời gian bay, sân bay trung gian, hạng vé.
- **Thống kê – Báo cáo** doanh thu theo tháng/tuyến bay, **xuất PDF**.
- **Thay đổi quy định** hệ thống (số sân bay, thời gian bay tối thiểu/tối đa, hạng vé, đơn giá, thời gian bán/đặt vé).
- **Email thông báo** sau khi thanh toán thành công.

> Use cases chính: Khách hàng đặt vé (UC01), Nhân viên bán vé (UC02), Lập lịch chuyến bay (UC03),
> Thống kê báo cáo (UC04), Thay đổi quy định (UC05).

---

## 🧩 Kiến trúc & Mô hình (UML/ERD)
- **Use Case Diagram** & đặc tả chi tiết cho 5 nhóm chức năng.
- **Class/Activity/Sequence Diagrams** mô tả luồng và tương tác.
- **ERD** các bảng điển hình: `flight_route`, `airport`, `flight`, `plane`, `ticket`, `seat`, `ticket_class`, `user`…

> Tham khảo thư mục `/docs` (nếu có) để xem hình UML/ERD.

---

## 🛠️ Công nghệ sử dụng
- **Backend/Frontend**: (tuỳ nhóm triển khai: ASP.NET MVC / Java / PHP, v.v.)
- **Database**: SQL Server hoặc MySQL
- **Charts**: Chart.js (thống kê)
- **Export**: PDF export
- **Payment**: Thanh toán online (ví dụ: PayOS/QR)

---

## 🚀 Cách chạy (gợi ý)
1. **Clone** repo:
   ```bash
   git clone https://github.com/<your-username>/FlightManagement.git
   cd FlightManagement
