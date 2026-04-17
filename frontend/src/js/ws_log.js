"use strict"

const logDiv = document.getElementById("log");

function log(msg, data = null) {
    const div = document.createElement("div");
    div.textContent =
        `[${new Date().toLocaleTimeString()}] ${msg}` +
        (data ? ` ${JSON.stringify(data)}` : "");

    logDiv.appendChild(div);
    logDiv.scrollTop = logDiv.scrollHeight;
}
