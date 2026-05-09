import { apiFetch } from "./api";

export interface CreateGamePayload {
  rounds: number;
  time: number;
  pack: number;
  password?: string | null;
}

export interface GameCreated {
  id: string;
  rounds: number;
  time: number;
  pack: number;
  password?: string | null;
}

export async function createGame(data: CreateGamePayload): Promise<GameCreated> {
  const res = await apiFetch("/api/v1/game", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text);
  }

  return res.json();
}

export class GameSocket {
  private socket: WebSocket;

  constructor(gameId: string, onMessage: (data: any) => void) {
    if (!gameId) throw new Error("gameId is required");

    const url = `/ws/game/${gameId}`;
    this.socket = new WebSocket(url);

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch {
        console.log("RAW WS:", event.data);
      }
    };
  }

  send(message: any) {
    this.socket.send(JSON.stringify(message));
  }

  close() {
    this.socket.close();
  }
}