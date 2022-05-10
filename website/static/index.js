function showPassword(password, button) {

    var password = document.getElementById(password);

    if (password.style.display === "none") {
      password.style.display = "block";
      document.getElementById(button).innerHTML = "Hide";
    } else {
      password.style.display = "none";
      document.getElementById(button).innerHTML = "Show";
    }
  }

function deletePassword(id) {

    fetch('/delete_password', {
    method: "POST",
    body: JSON.stringify({passId: id})
    }) .then((_res) => {
        window.location.href = "/";
    });
}
