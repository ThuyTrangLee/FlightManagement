const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const formal = document.querySelector(".formal");
const sign_in_btn2 = document.querySelector("#sign-in-btn2");
const sign_up_btn2 = document.querySelector("#sign-up-btn2");

const emailInput = document.getElementById('email');

// thuộc tính classList và phương thức add() để thêm lớp CSS có tên là sign-up-mode vào phần tử được lưu trữ trong biến formal.
sign_up_btn.addEventListener("click", () => {
  formal.classList.add("sign-up-mode");
});

// xóa lớp CSS có tên là sign-up-mode
sign_in_btn.addEventListener("click", () => {
  formal.classList.remove("sign-up-mode");
});
sign_up_btn2.addEventListener("click", () => {
  formal.classList.add("sign-up-mode2");
});
sign_in_btn2.addEventListener("click", () => {
  formal.classList.remove("sign-up-mode2");
});


