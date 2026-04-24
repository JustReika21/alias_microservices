import { useEffect, useState } from "react";
import { GameSocket } from "../services/gameService";
import type {GuessData} from "../types/game";

export function useGame(gameId: string) {
  const [players, setPlayers] = useState<any[]>([]);
  const [cards, setCards] = useState<any[]>([]);
  const [status, setStatus] = useState("setting_up");
  const [currentPlayer, setCurrentPlayer] = useState(false);
  const [guessedMap, setGuessedMap] = useState<Record<number, boolean>>({});
  const [logs, setLogs] = useState<string[]>([]);
  const [socket, setSocket] = useState<GameSocket | null>(null);

  function log(msg: string, data?: any) {
    const entry = `[${new Date().toLocaleTimeString()}] ${msg}` +
      (data ? ` ${JSON.stringify(data)}` : "");
    setLogs(prev => [...prev, entry]);
  }

  function resetGameState() {
    setCards([]);
    setGuessedMap({});
  }

  function applySnapshot(snapshot: any) {
    resetGameState();

    setStatus(snapshot.status);
    setCurrentPlayer(snapshot.current_player?.is_current || false);

    if (snapshot.cards) {
      setCards(snapshot.cards);

      if (snapshot.status === "calculating") {
        const map: Record<number, boolean> = {};
        snapshot.cards.forEach((c: any) => {
          map[c.id] = true;
        });
        setGuessedMap(map);
      }
    }

    log("snapshot", snapshot);
  }

  function handleMessage(data: any) {
    log("recv", data);

    switch (data.type) {
      case "snapshot":
        applySnapshot(data);
        break;

      case "players":
        setPlayers(data.players || []);
        break;

      case "current_player":
        setCurrentPlayer(data.is_current);
        break;

      case "status":
        setStatus(data.value);
        if (data.value === "waiting" || data.value === "started") resetGameState();
        break;

      case "card":
        if (data.card) {
          setCards(prev => [...prev, data.card]);
        }
        break;

      case "guess":
        setGuessedMap(prev => ({
          ...prev,
          [data.card]: data.guessed
        }));
        break;

      case "player_score_update":
        setPlayers(prev =>
          prev.map(p =>
            p.id == data.id ? { ...p, score: data.score } : p
          )
        );
        break;
    }
  }

  function sendGuess(guessData: GuessData) {
    socket?.send(guessData);
    log("send guess", guessData );
  }

  function sendAction(type: string) {
    socket?.send({ type });
    log("send action", type);
  }

  useEffect(() => {
    const s = new GameSocket(gameId, handleMessage);
    setSocket(s);
    return () => s.close();
  }, [gameId]);

  return {
    players,
    cards,
    status,
    currentPlayer,
    guessedMap,
    logs,
    sendGuess,
    sendAction
  };
}