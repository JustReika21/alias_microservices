const ACCESS_TOKEN_KEY = "access_token";

export async function registerUser(
  name: string,
  password: string
) {
  const res = await fetch("/api/v1/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name, password }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err);
  }

  return res.json();
}

export async function loginUser(
  name: string,
  password: string
) {
  const res = await fetch("/api/v1/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ name, password }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err);
  }

  const data = await res.json();

  localStorage.setItem(
    ACCESS_TOKEN_KEY,
    data.access_token
  );

  return data;
}

export async function logoutUser() {
  try {
    await fetch("/api/v1/auth/logout", {
      method: "POST",
      credentials: "include",
    });
  } catch (err) {
    console.error("Failed to fetch user:", err);
    return null;
  }

  localStorage.removeItem(
    ACCESS_TOKEN_KEY
  );
}

