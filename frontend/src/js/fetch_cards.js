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


async function fetchRandomCards(packId, limit = 10) {
    try {
        const response = await apiFetch(`/api/v1/packs/${packId}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pack_id: packId,
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const data = await response.json();
        console.log('Fetched cards:', data);

        return data;
    } catch (error) {
        console.error('Failed to fetch cards:', error);
        return [];
    }
}

function renderCards(cards) {
    const container = document.getElementById('cards-container');
    container.innerHTML = '';

    if (!cards.length) {
        container.innerHTML = '<p>No cards found</p>';
        return;
    }

    const list = document.createElement('ul');

    cards.forEach(card => {
        const item = document.createElement('li');
        item.textContent = `${card.id} - ${card.name ?? 'Unnamed card'}`;
        list.appendChild(item);
    });

    container.appendChild(list);
}

async function loadCards() {
    const packIdInput = document.getElementById('pack-id');
    const packId = parseInt(packIdInput.value, 10);

    if (Number.isNaN(packId)) {
        alert('Invalid pack_id');
        return;
    }

    const cards = await fetchRandomCards(packId, 100);
    renderCards(cards);
    // get_user()
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('load-btn')
        .addEventListener('click', loadCards);
});