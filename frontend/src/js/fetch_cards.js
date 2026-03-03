'use strict';

async function fetchRandomCards(packId, limit = 10) {
    try {
        const response = await fetch('/api/v1/cards/random', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pack_id: packId,
                limit: limit
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
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('load-btn')
        .addEventListener('click', loadCards);
});
