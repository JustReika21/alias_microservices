'use strict';

const startBtn = document.getElementById("start-btn");
const nextBtn = document.getElementById("next-btn");
const calculatedBtn = document.getElementById("calculated-btn");

const logDiv = document.getElementById("log");
const playersDiv = document.getElementById("players");
const cardsStackDiv = document.getElementById("cards-stack");

const gameId = window.location.pathname.split('/').filter(Boolean)[1];
const socket = new WebSocket(`/ws/game/${gameId}`);

// ================= STATE =================
let isCurrentPlayer = false;
let status = "setting_up";
let cards = [];
let guessedMap = {};

// ================= LOG =================
function log(msg, data = null) {
    if (!logDiv) return;

    const div = document.createElement("div");
    div.textContent =
        `[${new Date().toLocaleTimeString()}] ${msg}` +
        (data ? ` ${JSON.stringify(data)}` : "");

    logDiv.appendChild(div);
    logDiv.scrollTop = logDiv.scrollHeight;

    console.log(msg, data);
}

// ================= PLAYERS =================
function renderPlayers(players) {
    if (!players?.length) {
        playersDiv.textContent = "Players: empty";
        return;
    }

    playersDiv.innerHTML = players.map(p =>
        `<span class="player">${p.name} (${p.score})</span>`
    ).join("");
}

// ================= CONTROLS =================
function updateControls() {
    startBtn.style.display = "none";
    nextBtn.style.display = "none";
    calculatedBtn.style.display = "none";

    // 🔥 ONLY current_player affects these buttons
    if (!isCurrentPlayer) return;

    if (status === "waiting" || status === "setting_up") {
        startBtn.style.display = "inline-block";
    }

    else if (status === "started") {
        nextBtn.style.display = "inline-block";
    }

    else if (status === "calculating") {
        calculatedBtn.style.display = "inline-block";
    }
}

// ================= CARDS =================
function renderCards() {
    cardsStackDiv.innerHTML = "";

    for (const card of cards) {
        const div = document.createElement("div");
        div.className = "card-item";

        const state = guessedMap[card.id];

        if (state === true) div.classList.add("guessed");
        if (state === false) div.classList.add("not-guessed");

        div.textContent = card.word ?? "NONE";

        if (status === "calculating") {
            const actions = document.createElement("div");
            actions.className = "card-actions";

            const ok = document.createElement("button");
            ok.textContent = "GUESSED";
            ok.className = "guess-btn guessed-btn";
            ok.onclick = () => sendGuess(card.id, true);

            const no = document.createElement("button");
            no.textContent = "NOT GUESSED";
            no.className = "guess-btn not-guessed-btn";
            no.onclick = () => sendGuess(card.id, false);

            actions.appendChild(ok);
            actions.appendChild(no);
            div.appendChild(actions);
        }

        cardsStackDiv.appendChild(div);
    }
}

// ================= SEND GUESS =================
function sendGuess(cardId, guessed) {
    socket.send(JSON.stringify({
        type: guessed ? "guessed" : "not_guessed",
        card: cardId
    }));
}

// ================= RESET =================
function resetGameState() {
    cards = [];
    guessedMap = {};
    cardsStackDiv.innerHTML = "";
}

// ================= SOCKET =================
socket.onopen = () => log("SOCKET OPENED");
socket.onclose = () => log("SOCKET CLOSED");
socket.onerror = (e) => log("SOCKET ERROR", e);

socket.onmessage = (event) => {
    let data;

    try {
        data = JSON.parse(event.data);
    } catch {
        log("RAW", event.data);
        return;
    }

    log("RECEIVED", data);

    // ================= PLAYERS =================
    if (data.type === "players") {
        renderPlayers(data.players);
    }

    // ================= CURRENT PLAYER (ONLY UI CONTROL) =================
    else if (data.type === "current_player") {
        isCurrentPlayer = data.is_current;
        updateControls();
    }

    // ================= STATUS =================
    else if (data.type === "status") {
        status = data.value;

        if (status === "waiting") resetGameState();
        if (status === "started") resetGameState();

        renderCards();
        updateControls();
    }

    // ================= CARD =================
    else if (data.type === "card") {
        if (data.card) {
            cards.push(data.card);
            renderCards();
        }
    }

    // ================= GUESS (GLOBAL STATE) =================
    else if (data.type === "guess") {
        guessedMap[data.card] = data.guessed;
        renderCards();
    }

    else if (data.type === "kick") {
        alert("KICKED");
        socket.close();
    }
};

// ================= ACTIONS =================
startBtn.onclick = () =>
    socket.send(JSON.stringify({ type: "start" }));

nextBtn.onclick = () =>
    socket.send(JSON.stringify({ type: "next" }));

calculatedBtn.onclick = () =>
    socket.send(JSON.stringify({ type: "calculated" }));