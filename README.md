# ✈️ Flight Management System

Hệ thống **Quản lý chuyến bay** hỗ trợ khách hàng và nhân viên trong việc đặt vé, bán vé, lập lịch chuyến bay, thống kê doanh thu và quản trị quy định.  
*Software Engineering – Course Project.*

---

## 📌 Tính năng chính
- **Đặt vé trực tuyến**: tìm chuyến bay → chọn ghế → thanh toán online → nhận e‑ticket qua email.
- **Tra cứu chuyến bay** theo tuyến, ngày đi/về.
- **Nhân viên bán vé** tại quầy (nhập thông tin khách, xác nhận thanh toán).
- **Lập lịch chuyến bay**: thời gian bay, sân bay trung gian, hạng vé.
- **Thống kê – Báo cáo** doanh thu theo tháng/tuyến; **xuất PDF**.
- **Quản trị quy định**: số sân bay, thời gian bay tối thiểu/tối đa, hạng vé, đơn giá, thời gian bán/đặt vé.

> Use cases: Khách hàng đặt vé (UC01), Nhân viên bán vé (UC02), Lập lịch (UC03), Thống kê (UC04), Thay đổi quy định (UC05).

---

## 🛠️ Công nghệ sử dụng
- Ngôn ngữ: Python, HTML, CSS, JavaScript  
- Môi trường phát triển: PyCharm, MySQL
- Công cụ mô hình hóa: Astah UML (Use ase, Class Diagram, Activity Diagram, Sequence Diagram), ERD
- Công cụ trực quan hóa: ChartJS (thống kê, báo cáo) 
- Xuất báo cáo: PDF Export
- Thanh toán: QR Code

---

## 🧩 Kiến trúc & Mô hình
- **Use Case & đặc tả** cho 5 nhóm chức năng.
- **UML**: Class / Activity / Sequence để mô tả luồng & tương tác.
- **ERD** cho các thực thể: `flight_route`, `airport`, `flight`, `plane`, `ticket`, `seat`, `ticket_class`, `user`, …

---
