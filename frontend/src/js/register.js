async function register() {
  const name = document.getElementById("name").value;
  const password = document.getElementById("password").value;
  const msg = document.getElementById("msg");

  msg.innerText = "Loading...";

  try {
    const res = await fetch("/api/v1/auth/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name,
        password
      })
    });

    if (!res.ok) {
      const err = await res.text();
      msg.innerText = "Error: " + err;
      return;
    }

    msg.innerText = "Registered successfully!";
  } catch (e) {
    msg.innerText = "Network error";
  }
}