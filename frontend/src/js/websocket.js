// /static/js/websocket.js

const input = document.getElementById("data");
const button = document.getElementById("data-btn");
const container = document.getElementById("cards-container");

const gameId = document.body.dataset.gameId || "test";

const wsUrl = '/ws/game/test';

const socket = new WebSocket(wsUrl);

socket.onopen = () => {
    console.log("WebSocket connected:", wsUrl);
};

socket.onmessage = (event) => {
    const message = event.data;

    const div = document.createElement("div");
    div.textContent = message;

    container.appendChild(div);
};

socket.onerror = (error) => {
    console.error("WebSocket error:", error);
};

socket.onclose = () => {
    console.log("WebSocket closed");
};

button.addEventListener("click", () => {
    const value = input.value.trim();
    if (!value) return;

    if (socket.readyState === WebSocket.OPEN) {
        socket.send(value);
    } else {
        console.error("WebSocket is not open");
    }

    input.value = "";
});