'use strict';

import { apiFetch } from './auth.js';

async function createGame(gameData) {
    let res;

    try {
        res = await apiFetch('/api/v1/game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(gameData)
        });
    } catch (e) {
        document.getElementById('result').innerText = 'Session expired';
        return;
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