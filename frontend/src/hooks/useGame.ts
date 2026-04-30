import { useEffect, useState } from "react";
import { GameSocket } from "../services/gameService";
import type { GuessData } from "../types/game";
import type { Player, Team } from "../types/team";

export function useGame(gameId: string) {
  const [players, setPlayers] = useState<Player[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [cards, setCards] = useState<any[]>([]);
  const [status, setStatus] = useState("setting_up");

  const [myId, setMyId] = useState<string | null>(null);
  const [currentPlayerId, setCurrentPlayerId] = useState<string | null>(null);

  const [guessedMap, setGuessedMap] = useState<Record<number, boolean>>({});
  const [logs, setLogs] = useState<string[]>([]);
  const [endTime, setEndTime] = useState<number | null>(null);
  const [socket, setSocket] = useState<GameSocket | null>(null);

  const isMyTurn = myId !== null && currentPlayerId === myId;

  function log(msg: string, data?: unknown) {
    const entry =
      `[${new Date().toLocaleTimeString()}] ${msg}` +
      (data ? ` ${JSON.stringify(data)}` : "");
    setLogs((prev) => [...prev, entry]);
  }

  function resetGameState() {
    setCards([]);
    setGuessedMap({});
    setEndTime(null);
  }

  function normalizePlayer(p: any): Player {
    return {
      id: String(p.id),
      name: p.name,
      score: Number(p.score),
      teamId: String(p.team_id),
    };
  }

  function normalizeTeam(t: any): Team {
    return {
      id: String(t.id),
      totalPlayers: Number(t.total_players),
      score: Number(t.score),
    };
  }

  function applySnapshot(snapshot: any) {
    resetGameState();

    setStatus(snapshot.status);

    if (snapshot.current_player?.player_id) {
      setCurrentPlayerId(String(snapshot.current_player.player_id));
    }

    if (snapshot.players) setPlayers(snapshot.players.map(normalizePlayer));
    if (snapshot.teams) setTeams(snapshot.teams.map(normalizeTeam));
    if (snapshot.cards) setCards(snapshot.cards);

    if (snapshot.end_time) setEndTime(snapshot.end_time);

    if (snapshot.status === "calculating" && snapshot.cards) {
      const map: Record<number, boolean> = {};
      snapshot.cards.forEach((c: any) => (map[c.id] = true));
      setGuessedMap(map);
    }

    log("snapshot", snapshot);
  }

  function handleMessage(data: any) {
    log("recv", data);

    switch (data.type) {
      case "my_id":
        setMyId(String(data.my_id));
        break;

      case "snapshot":
        applySnapshot(data);
        break;

      case "players":
        setPlayers((data.players || []).map(normalizePlayer));
        break;

      case "teams":
        setTeams((data.teams || []).map(normalizeTeam));
        break;

      case "team_score_update":
        setTeams((prev) =>
          prev.map((t) =>
            t.id === String(data.id)
              ? { ...t, score: Number(data.score) }
              : t
          )
        );
        break;

      case "player_score_update":
        setPlayers((prev) =>
          prev.map((p) =>
            p.id === String(data.id)
              ? { ...p, score: Number(data.score) }
              : p
          )
        );
        break;

      case "current_player":
        setCurrentPlayerId(String(data.player_id));
        break;

      case "status":
        setStatus(data.value);
        if (data.value === "waiting" || data.value === "started") {
          resetGameState();
        }
        break;

      case "card":
        if (data.card) setCards((prev) => [...prev, data.card]);
        break;

      case "guess":
        setGuessedMap((prev) => ({
          ...prev,
          [data.card]: data.guessed,
        }));
        break;

      case "timer":
        setEndTime(data.end_time);
        break;
    }
  }

  function sendGuess(guessData: GuessData) {
    socket?.send(guessData);
    log("send guess", guessData);
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
    teams,
    cards,
    status,
    isMyTurn,
    myId,
    currentPlayerId,
    guessedMap,
    logs,
    endTime,
    sendGuess,
    sendAction,
  };
}