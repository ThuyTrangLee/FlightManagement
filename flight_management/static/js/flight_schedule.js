document.addEventListener('DOMContentLoaded', function () {
    var ticketsData = [];
    document.getElementById("themmmmmm").addEventListener("click", addTicket);
    function addTicket() {
        const ticketClass = document.getElementById('ticket_class').value;
        const quantity = parseInt(document.getElementById('quantity').value);
        const ticketPrice = parseInt(document.getElementById('ticket_price').value);

        const currentRowCount = document.querySelectorAll('#ticketList .ticket-row').length;

        const currentRow = Array.from(document.querySelectorAll('#ticketList .ticket-row'))

        if (currentRowCount < {{ nuticketclass }} || currentRow.some(row => row.dataset.ticketClass === ticketClass)) {
            if (ticketClass && quantity &&ticketPrice) {
                let existingTicket = false;

                // Lặp qua từng dòng trong danh sách vé
                document.querySelectorAll('#ticketList .ticket-row').forEach(function (row) {
                    // Kiểm tra nếu hạng ghế đã tồn tại
                    if (row.dataset.ticketClass === ticketClass) {
                        // Tăng số lượng cho hạng ghế đó
                        const currentQuantity = parseInt(row.querySelector('.ticket-quantity').value);
                        row.querySelector('.ticket-quantity').value = currentQuantity + quantity;
                        row.querySelector('.ticket-price').value = ticketPrice;
                        existingTicket = true;
                    }
                });
                 ticketsData.push({
                    ticketClass: ticketClass,
                    quantity: quantity,
                    ticketPrice: ticketPrice
                });

                // Nếu hạng ghế không tồn tại trong danh sách, thêm mới

                if (!existingTicket) {
                    const ticketItem = `
                        <div class="row m-2 ticket-row" data-ticket-class="${ticketClass}">
                            <div class="col-md-3">
                                <input type="text" class="form-control" value="${ticketClass}" readonly>
                            </div>
                            <div class="col-md-3">
                                <input type="number" class="form-control ticket-quantity" value="${quantity}" readonly>
                            </div>
                            <div class="col-md-3">
                                <input type="number" class="form-control ticket-price" value="${ticketPrice}" readonly>
                            </div>
                            <div class="col-md-3 align-self-end">
                                <button type="button" class="btn btn-danger" onclick="removeTicket(this)">Xóa</button>
                            </div>
                        </div>
                    `;
                    document.getElementById('ticketList').insertAdjacentHTML('beforeend', ticketItem);
                }

                document.getElementById('ticketForm').reset();
            } else {
                alert('Please select ticket class and enter quantity.');
            }
         } else {
            alert('You cannot add more than 3 tickets.');
        }
    }

    function removeTicket(button) {
        const ticketClass = button.closest('.ticket-row').dataset.ticketClass;
        // Remove the ticket from the ticketsData array
        ticketsData = ticketsData.filter(ticket => ticket.ticketClass !== ticketClass);
        button.closest('.ticket-row').remove();
    }
// Khai báo biến toàn cục để lưu trữ dữ liệu các sân bay trung gian
    var imAirport = [];

    // Hàm để thêm hàng vào bảng dựa trên số lượng sân bay trung gian
    function addIntermediateAirportsRows(count) {
        const table = document.getElementById('intermediateAirportTable');

        // Xóa các hàng hiện có trước khi thêm mới
        table.innerHTML = `
            <tr>
                <th>STT</th>
                <th>Sân bay trung gian</th>
                <th>Thời gian dừng</th>
                <th>Ghi chú</th>
            </tr>
        `;

        // Thêm các hàng mới
        for (let i = 1; i <= count; i++) {
            table.innerHTML += `
                <tr>
                    <td>${i}</td>
                    <td>
                        <select class="form-control" id="imairport_${i}" aria-label="Default select example">
                            <option value="" selected disabled>Sân bay trung gian</option>
                            <!-- Lặp qua danh sách sân bay và tạo các option -->
                            {% for i in airport %}
                                <option value="{{ i.id }}">{{ i }}</option>
                            {% endfor %}
                        </select>
                    </td>
                    <td><input type="number" class="form-control" id="duration_${i}" name="duration_${i}" step="10" min="{{ minstop }}"></td>
                    <td><input type="text" class="form-control" id="note_${i}" name="note_${i}"></td>
                </tr>
            `;
        }
    }

    // Gọi hàm khi trang được tải (có thể thay đổi số lượng sân bay trung gian mặc định ở đây)
    window.onload = function () {
        const defaultIntermediateAirportsCount = {{ maxinairport }}; // Số lượng sân bay trung gian mặc định
        addIntermediateAirportsRows(defaultIntermediateAirportsCount);
    };

    // Hàm để tạo lịch trình chuyến bay
    function createFlightSchedule() {

        imAirport = [];
        for (let i = 1; i <= {{ maxinairport }}; i++) {
            const airportId = document.getElementById(`imairport_${i}`).value;
            const duration = document.getElementById(`duration_${i}`).value;
            const note = document.getElementById(`note_${i}`).value;

            // Chỉ thêm dữ liệu nếu đã chọn sân bay và thời gian dừng
            if (airportId && duration) {
                imAirport.push({
                    airportId: airportId,
                    duration: duration,
                    note: note
                });
            }
        }

        // Gán thông tin vé từ giao diện người dùng vào biến toàn cục (nếu cần)
        document.getElementById('tickets_data').value = JSON.stringify(ticketsData);

        // Gán thông tin sân bay trung gian vào trường ẩn trong form
        document.getElementById('im_airport').value = JSON.stringify(imAirport);

        // Gửi form đi
        document.getElementById('ticketForm').submit();
    }
});