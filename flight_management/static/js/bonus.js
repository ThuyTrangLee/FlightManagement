//slide
document.addEventListener("DOMContentLoaded", () => {
  //thêm icon thành hai nút điều hướng slide
  const navText = [
    "<i class='bx bx-chevron-left'></i>",
    "<i class='bx bx-chevron-right'></i>",
  ];

  $("#hero-carousel").owlCarousel({
    items: 1, //Số lượng mục hiển thị trên một trang
    dots: false, //tắt nút chuyển slide
    loop: true, //quay lại slide ban đầu
    nav: true, //bật thanh điều hướng slide
    navText: navText, //sử dụng nội dung trong `navtext` để làm nút điều hướng
    autoplay: true, //tự động chuyển slide, có thể set time = autoplayTimeout:1000
    autoplayTimeout: 5000,
    autoPlayHoverPause: true, //tự động dừng khi rê chuột vào slide
  });
});