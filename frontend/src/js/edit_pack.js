'use strict';

import { apiFetch } from './auth.js';

const match = window.location.pathname.match(/\/pack\/edit\/(\d+)/);
const packId = match ? parseInt(match[1]) : null;

if (!packId) {
    alert('Pack ID not found in URL');
    throw new Error('Pack ID not found');
}

async function fetchPack() {
    const res = await apiFetch(`/api/v1/packs/edit/${packId}`);
    if (!res.ok) throw new Error('Pack not found');
    return res.json();
}

async function fetchCards() {
    const res = await apiFetch(`/api/v1/cards`, {
        method: 'POST', // pack_id теперь в body
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pack_id: packId })
    });
    if (!res.ok) throw new Error('Failed to fetch cards');
    return res.json();
}

async function loadPackAndCards() {
    try {
        const pack = await fetchPack();
        document.getElementById('pack-name').value = pack.name;
        document.getElementById('pack-description').value = pack.description;

        const cards = await fetchCards();
        renderCards(cards);
    } catch (e) {
        alert('Error loading pack or cards');
        console.error(e);
    }
}

function renderCards(cards) {
    const list = document.getElementById('cards-list');
    list.innerHTML = '';
    cards.forEach(card => {
        const li = document.createElement('li');
        li.textContent = card.word;

        const delBtn = document.createElement('button');
        delBtn.textContent = 'Delete';
        delBtn.addEventListener('click', async () => {
            if (!confirm(`Delete card "${card.word}"?`)) return;
            try {
                await deleteCard(card.id);
                loadPackAndCards();
            } catch (e) {
                alert('Error deleting card');
            }
        });

        li.appendChild(delBtn);
        list.appendChild(li);
    });
}

// Остальной код (updatePack, addCard, deleteCard) без изменений

document.getElementById('pack-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('pack-name').value.trim();
    const description = document.getElementById('pack-description').value.trim();
    try {
        await updatePack(name, description);
        alert('Pack updated successfully');
    } catch (e) {
        alert('Error updating pack');
    }
});

document.getElementById('add-card-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const wordInput = document.getElementById('new-card-word');
    const word = wordInput.value.trim();
    if (!word) return;
    try {
        await addCard(word);
        wordInput.value = '';
        loadPackAndCards();
    } catch (e) {
        alert('Error adding card');
    }
});

// Инициализация
loadPackAndCards();