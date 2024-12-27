document.addEventListener('DOMContentLoaded', function() {
    var checkbox = document.getElementById('flexSwitchCheckChecked');
    var table = document.getElementById('tuychonsanbaytrungian');
    var flight_time = document.getElementById('flight_time');
    var sum_flight_time = document.getElementById('sum_flight_time');
    sum_flight_time.value = flight_time.value
    var form = document.getElementById('myForm');
    var isChecked = false;
    var selects = document.querySelectorAll('select[id^="sanbaytrunggian-"]');
    var flightSettingsElement = document.getElementById('flightSettings');
    var maxStopoverAirports = flightSettingsElement.getAttribute('data-max-stopovers');
    const airportsCount = maxStopoverAirports; // Dynamically get from Flask
    // Hàm để hiển thị hoặc ẩn form khi checkbox thay đổi trạng thái
    checkbox.addEventListener('change', function() {

        // Kiểm tra trạng thái của checkbox
        if (this.checked) {
            table.style.display = 'block';  // Hiển thị form nếu checkbox được chọn
            calculate()
        } else {
            table.style.display = 'none';   // Ẩn form nếu checkbox không được chọn
            sum_flight_time.value=flight_time.value
        }
    });

        flight_time.addEventListener('change', function () {
            let sum = 0;
            if (isChecked) {
                for (let i = 1; i <= airportsCount; i++) {
                    let stopTimeInput = document.getElementById(`thoigiandung-${i}`);
                    let select = document.getElementById(`sanbaytrunggian-${i}`);
                    if (!stopTimeInput.disabled && select.value !== '0') {
                        sum += parseInt(stopTimeInput.value) ;
                    }
                }
                sum_flight_time.value = parseInt(flight_time.value) + sum;
            } else {
                sum_flight_time.value = flight_time.value;
            }
        });

    for (let i = 1; i <= airportsCount; i++) {
        let select = document.getElementById(`sanbaytrunggian-${i}`);
        let stopTimeInput = document.getElementById(`thoigiandung-${i}`);


        select.addEventListener('change', function () {
            if (!stopTimeInput.disabled && select.value === '0') {
                let currentSum = parseInt(sum_flight_time.value) || 0;
                sum_flight_time.value = currentSum - (parseInt(stopTimeInput.value) || 0);
            }
        });
    }



    function calculate() {
        let sum = parseInt(flight_time.value);
            for (let i = 1; i <= airportsCount; i++) {
            let stopTimeInput = document.getElementById(`thoigiandung-${i}`);
            console.log(stopTimeInput.value)
            if (!stopTimeInput.disabled) {
                sum += parseInt(stopTimeInput.value);
            }
        }
        if(checkbox.checked){
            isChecked = true
            sum_flight_time.value = sum
        }
        return sum;

    }

    for (let i = 1; i <= airportsCount; i++) {
        let select = document.getElementById(`sanbaytrunggian-${i}`);
        let stopTimeInput = document.getElementById(`thoigiandung-${i}`);
        let notesInput = document.getElementById(`ghichu-${i}`);



        function toggleInputs() {
            if (select.value === '0') {
                stopTimeInput.disabled = true;
                notesInput.disabled = true;
            } else {
                stopTimeInput.disabled = false;
                notesInput.disabled = false;
                calculate()
            }
        }

        select.addEventListener('change', toggleInputs);
        stopTimeInput.addEventListener('input', calculate);
        toggleInputs();
    }
    form.addEventListener('submit', function(event) {
        // Ngăn việc gửi form mặc định (nếu cần)
        event.preventDefault();
        flight_time.disabled = false;
        form.submit();
    });
});
