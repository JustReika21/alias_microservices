'use strict';

async function refreshAccessToken() {
    const res = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
        credentials: 'include'
    });

    if (!res.ok) {
        throw new Error('Refresh failed');
    }

    const data = await res.json();
    localStorage.setItem('access_token', data.access_token);

    return data.access_token;
}

async function apiFetch(url, options = {}) {
    let token = localStorage.getItem('access_token');

    let res = await fetch(url, {
        ...options,
        credentials: 'include',
        headers: {
            ...(options.headers || {}),
            ...(token ? { Authorization: `Bearer ${token}` } : {})
        }
    });

    if (res.status === 401) {
        try {
            token = await refreshAccessToken();

            res = await fetch(url, {
                ...options,
                credentials: 'include',
                headers: {
                    ...(options.headers || {}),
                    Authorization: `Bearer ${token}`
                }
            });
        } catch (e) {
            localStorage.removeItem('access_token');
            window.location.href = '/login';
            throw e;
        }
    }

    return res;
}

async function get_user() {
    try {
        const response = await apiFetch('/api/v1/auth/me', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        console.log('user:', data);

        return data;
    } catch (error) {
        console.error('Failed to fetch cards:', error);
        return [];
    }
}

export { apiFetch, refreshAccessToken, get_user };