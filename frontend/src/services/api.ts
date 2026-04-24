const ACCESS_TOKEN_KEY = "access_token";

async function refreshAccessToken() {
  const res = await fetch("/api/v1/auth/refresh", {
    method: "POST",
    credentials: "include",
  });

  if (res.status != 200) throw new Error("Not authenticated");

  const data = await res.json();
  localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
  return data.access_token;
}

async function apiFetch(url: string, options: RequestInit = {}) {
  let token = localStorage.getItem(ACCESS_TOKEN_KEY);

  let res = await fetch(url, {
    ...options,
    credentials: "include",
    headers: {
      ...(options.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });

  if (res.status === 401) {
    try {
      token = await refreshAccessToken();

      res = await fetch(url, {
        ...options,
        credentials: "include",
        headers: {
          ...(options.headers || {}),
          Authorization: `Bearer ${token}`,
        },
      });
    } catch (e) {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      window.location.href = "/login";
      throw e;
    }
  }

  return res;
}

async function getUser() {
  try {
    const res = await apiFetch("/api/v1/auth/me", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });

    return await res.json();
  } catch (err) {
    console.error("Failed to fetch user:", err);
    return null;
  }
}

export { apiFetch, refreshAccessToken, getUser };