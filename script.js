// 다크모드 전환. JS는 body에 dark 클래스를 붙였다 뗄 뿐이고,
// 실제 색이 바뀌는 것은 CSS가 그 클래스에 스타일을 정의해 두었기 때문이다.

// 이전에 고른 테마를 기억해 두 페이지에서 같게 유지한다.
if (localStorage.getItem("theme") === "dark") {
  document.body.classList.add("dark");
}

const btn = document.querySelector("#theme-btn");
if (btn) {
  btn.addEventListener("click", () => {
    const isDark = document.body.classList.toggle("dark");
    localStorage.setItem("theme", isDark ? "dark" : "light");
  });
}
