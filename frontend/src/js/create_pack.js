'use strict';

import { apiFetch } from './auth.js';

const form = document.getElementById('packForm');
const result = document.getElementById('result');

async function createPack(packData) {
    let res;

    try {
        res = await apiFetch('/api/v1/packs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(packData)
        });
    } catch (e) {
        result.innerText = 'Session expired';
        return;
    }

    if (!res.ok) {
        const text = await res.text();
        result.innerText = 'Error: ' + text;
        return;
    }

    const data = await res.json();
    window.location.href = `/pack/edit/${data.id}`;
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const packData = {
        name: document.getElementById('name').value.trim(),
        description: document.getElementById('description').value.trim() || null
    };

    await createPack(packData);
});