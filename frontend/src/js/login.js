window.register = async function () {
  const name = document.getElementById("name").value;
  const password = document.getElementById("password").value;
  const msg = document.getElementById("msg");

  msg.innerText = "Loading...";

  try {
    const res = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name: name,
        password: password
      })
    });

    if (!res.ok) {
      const err = await res.text();
      msg.innerText = "Error: " + err;
      return;
    }

    const data = await res.json();

    localStorage.setItem("access_token", data.access_token);

    msg.innerText = "Success!";
  } catch (e) {
    msg.innerText = "Network error";
  }
};