const ACCESS_TOKEN_KEY = "access_token";

let isRefreshing = false;
let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken() {
  const res = await fetch("/api/v1/auth/refresh", {
    method: "POST",
    credentials: "include",
  });

  if (res.status !== 200) {
    throw new Error("Not authenticated");
  }

  const data = await res.json();

  localStorage.setItem(
    ACCESS_TOKEN_KEY,
    data.access_token
  );

  return data.access_token;
}

async function apiFetch(
  url: string,
  options: RequestInit = {}
) {
  let token = localStorage.getItem(
    ACCESS_TOKEN_KEY
  );

  let res = await fetch(url, {
    ...options,
    credentials: "include",
    headers: {
      ...(options.headers || {}),
      ...(token
        ? { Authorization: `Bearer ${token}` }
        : {}),
    },
  });

  if (res.status !== 401) {
    return res;
  }

  if (!isRefreshing) {
    isRefreshing = true;
    refreshPromise = refreshAccessToken().finally(() => {
      isRefreshing = false;
    });
  }

  try {
    token = await refreshPromise!;
  } catch (e) {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    throw e;
  }

  res = await fetch(url, {
    ...options,
    credentials: "include",
    headers: {
      ...(options.headers || {}),
      ...(token
        ? { Authorization: `Bearer ${token}` }
        : {}),
    },
  });

  return res;
}

async function getUser() {
  try {
    const res = await apiFetch(
      "/api/v1/auth/me",
      { method: "GET" }
    );

    if (!res.ok) {
      return null;
    }

    return await res.json();
  } catch {
    return null;
  }
}

export {
  apiFetch,
  refreshAccessToken,
  getUser,
};
