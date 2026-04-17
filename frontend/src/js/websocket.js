"use strict"

const setUpBtn = document.getElementById("set-up-btn")
const startBtn = document.getElementById("start-btn");
const nextBtn = document.getElementById("next-btn");
const calculatedBtn = document.getElementById("calculated-btn");


const playersDiv = document.getElementById("players");
const cardsStackDiv = document.getElementById("cards-stack");

const gameId = window.location.pathname.split('/').filter(Boolean)[1];
const socket = new WebSocket(`/ws/game/${gameId}`);

// ================= STATE =================
let isCurrentPlayer = false;
let status = "setting_up";

let cards = [];
let guessedMap = {};
let playersMap = {};

// ================= PLAYERS =================
function renderPlayers() {
    const players = Object.values(playersMap);

    if (!players.length) {
        playersDiv.textContent = "Players: empty";
        return;
    }

    playersDiv.innerHTML = players
        .map(p => `<span class="player">${p.name} (${p.score})</span>`)
        .join("");
}

// ================= CONTROLS =================
function updateControls() {
    setUpBtn.style.display = "none"
    startBtn.style.display = "none";
    nextBtn.style.display = "none";
    calculatedBtn.style.display = "none";

    if (!isCurrentPlayer) return;

    if (status === "setting_up") {
        setUpBtn.style.display = "inline-block"
    }

    if (status === "waiting") {
        startBtn.style.display = "inline-block";
    }

    if (status === "started") {
        nextBtn.style.display = "inline-block";
    }

    if (status === "calculating") {
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

// ================= GUESS =================
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

// ================= AUTO MARK =================
function markAllCardsAsGuessed() {
    for (const card of cards) {
        guessedMap[card.id] = true;
    }
}

// ================= SNAPSHOT =================
function applySnapshot(snapshot) {
    resetGameState();

    status = snapshot.status;
    isCurrentPlayer = snapshot.current_player.is_current;

    if (snapshot.cards) {
        cards = snapshot.cards;

        if (status === "calculating") {
            markAllCardsAsGuessed();
        }
    }

    renderCards();
    updateControls();
}

// ================= SOCKET =================
socket.onmessage = (event) => {
    let data;

    try {
        data = JSON.parse(event.data);
    } catch {
        log("RAW", event.data);
        return;
    }

    log("RECEIVED", data);

    // ✅ SNAPSHOT (highest priority)
    if (data.type === "snapshot") {
        applySnapshot(data);
        return;
    }

    // PLAYERS INIT
    if (data.type === "players") {
        playersMap = {};

        for (const p of data.players) {
            playersMap[p.id] = p;
        }

        renderPlayers();
    }

    // CURRENT PLAYER
    else if (data.type === "current_player") {
        isCurrentPlayer = data.is_current;
        updateControls();
    }

    // STATUS
    else if (data.type === "status") {
        status = data.value;

        if (status === "waiting" || status === "started") {
            resetGameState();
        }

        if (status === "calculating") {
            markAllCardsAsGuessed();
        }

        renderCards();
        updateControls();
    }

    // CARD
    else if (data.type === "card") {
        if (data.card) {
            cards.push(data.card);

            if (status === "calculating") {
                guessedMap[data.card.id] = true;
            }

            renderCards();
        }
    }

    // GUESS
    else if (data.type === "guess") {
        guessedMap[data.card] = data.guessed;
        renderCards();
    }

    // SCORE
    else if (data.type === "player_score_update") {
        const p = playersMap[data.id];
        if (p) {
            p.score = data.score;
        }
        renderPlayers();
    }

    // KICK
    else if (data.type === "kick") {
        alert("KICKED");
        socket.close();
    }
};

// ================= ACTIONS =================
setUpBtn.onclick = () =>
    socket.send(JSON.stringify({ type: "set_up" }));

startBtn.onclick = () =>
    socket.send(JSON.stringify({ type: "start" }));

nextBtn.onclick = () =>
    socket.send(JSON.stringify({ type: "next" }));

calculatedBtn.onclick = () =>
    socket.send(JSON.stringify({ type: "calculated" }));