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

async function getAccessToken() {
    let token = localStorage.getItem('access_token');

    if (!token) {
        token = await refreshAccessToken();
    }

    return token;
}

async function createGame(gameData) {
    let token;

    try {
        token = await getAccessToken();
    } catch (e) {
        document.getElementById('result').innerText = 'Auth error';
        return;
    }

    let res = await fetch('/api/v1/game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        credentials: 'include',
        body: JSON.stringify(gameData)
    });

    if (res.status === 401) {
        try {
            token = await refreshAccessToken();

            res = await fetch('/api/v1/game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                credentials: 'include',
                body: JSON.stringify(gameData)
            });
        } catch (e) {
            document.getElementById('result').innerText = 'Session expired';
            return;
        }
    }

    if (!res.ok) {
        const text = await res.text();
        document.getElementById('result').innerText = 'Error: ' + text;
        return;
    }

    document.getElementById('result').innerText = 'Game created!';
}

document.getElementById('gameForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const gameData = {
        rounds: parseInt(document.getElementById('rounds').value),
        time: parseInt(document.getElementById('time').value),
        pack: parseInt(document.getElementById('pack').value),
        password: document.getElementById('password').value || null
    };

    await createGame(gameData);
});