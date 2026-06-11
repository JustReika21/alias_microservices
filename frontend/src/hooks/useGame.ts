import { useEffect, useState } from "react";
import { GameSocket } from "../services/gameService";
import type { GuessData, SwitchData } from "../types/game";
import type { Player, Team } from "../types/team";
import type { Status } from "../types/game_button";

type Snapshot = {
  type: "snapshot";
  my_id: number;
  host: number;
  status: string;
  current_player: {
    player_id: number;
    is_current: boolean;
  };
  players: any[];
  teams: any[];
  cards: any[] | null;
  end_time?: number;
  winners?: string[] | number[] | null;
};

export function useGame(gameId: string) {
  const [players, setPlayers] = useState<Player[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [cards, setCards] = useState<any[]>([]);
  const [status, setStatus] = useState<Status>("setting_up");

  const [myId, setMyId] = useState<string | null>(null);
  const [hostId, setHostId] = useState<string | null>(null);
  const [currentPlayerId, setCurrentPlayerId] = useState<string | null>(null);

  const [guessedMap, setGuessedMap] = useState<Record<number, boolean>>({});
  const [logs, setLogs] = useState<string[]>([]);
  const [endTime, setEndTime] = useState<number | null>(null);
  const [socket, setSocket] = useState<GameSocket | null>(null);

  const [winners, setWinners] = useState<string[]>([]);
  const [isDraw, setIsDraw] = useState(false);

  const isMyTurn =
    myId !== null &&
    currentPlayerId !== null &&
    String(currentPlayerId) === String(myId);

  function log(msg: string, data?: unknown) {
    setLogs((prev) => [
      ...prev,
      `[${new Date().toLocaleTimeString()}] ${msg}` +
        (data ? ` ${JSON.stringify(data)}` : ""),
    ]);
  }

  function resetGameState() {
    setCards([]);
    setGuessedMap({});
    setEndTime(null);
    setWinners([]);
    setIsDraw(false);
  }

  function normalizePlayer(p: any): Player {
    return {
      id: String(p.id),
      name: p.name,
      score: Number(p.score),
      teamId: String(p.team_id),

      connected:
        p.connected === true ||
        p.connected === 1 ||
        p.connected === "1",
    };
  }

  function normalizeTeam(t: any): Team {
    return {
      id: String(t.id),
      totalPlayers: Number(t.total_players),
      score: Number(t.score),
    };
  }

  function applySnapshot(snapshot: Snapshot) {
    resetGameState();

    setStatus(snapshot.status as Status);

    if (snapshot.my_id !== undefined) setMyId(String(snapshot.my_id));
    if (snapshot.host !== undefined) setHostId(String(snapshot.host));

    if (snapshot.current_player?.player_id !== undefined) {
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

    if (snapshot.status === "finished" && snapshot.winners) {
      const winnerIds = snapshot.winners.map(String);
      setWinners(winnerIds);
      setIsDraw(winnerIds.length > 1);
    }

    log("snapshot", snapshot);
  }

  function handleMessage(data: any) {
    log("recv", data);

    switch (data.type) {
      case "snapshot":
        applySnapshot(data);
        break;

      case "player_joined": {
        if (!data.player) return;

        const incoming = normalizePlayer(data.player);

        setPlayers((prev) => {
          const exists = prev.some((p) => p.id === incoming.id);

          if (!exists) return [...prev, incoming];

          return prev.map((p) =>
            p.id === incoming.id
              ? { ...p, ...incoming, connected: true }
              : p
          );
        });

        break;
      }

      case "player_disconnected":
        setPlayers((prev) =>
          prev.map((p) =>
            p.id === String(data.user_id)
              ? { ...p, connected: false }
              : p
          )
        );
        break;

      case "player_kicked":
        setPlayers((prev) => {
          const updated = prev.filter(
            (p) => p.id !== String(data.user_id)
          );

          setTeams((tprev) =>
            tprev.map((t) => ({
              ...t,
              totalPlayers: updated.filter(
                (p) => p.teamId === t.id
              ).length,
            }))
          );

          return updated;
        });

        if (currentPlayerId === String(data.user_id)) {
          setCurrentPlayerId(null);
        }

        if (hostId === String(data.user_id)) {
          setHostId(null);
        }

        break;

      case "you_have_been_kicked":
        socket?.close();
        window.location.href = "/";
        break;

      case "player_switch_team":
        setPlayers((prev) => {
          const player = prev.find(
            (p) => p.id === String(data.player_id)
          );

          if (!player) return prev;

          return prev.map((p) =>
            p.id === String(data.player_id)
              ? { ...p, teamId: String(data.new_team_id) }
              : p
          );
        });

        if (data.current_player_id !== undefined) {
          setCurrentPlayerId(String(data.current_player_id));
        }

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
        setStatus(data.value as Status);

        if (
          ["setting_up", "waiting", "started"].includes(
            data.value
          )
        ) {
          resetGameState();
        }
        break;

      case "card":
        if (data.card) {
          setCards((prev) => [...prev, data.card]);
        }
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

      case "end_game": {
        const winnerIds = (data.winners || []).map(String);
        setStatus("finished");
        setWinners(winnerIds);
        setIsDraw(winnerIds.length > 1);
        break;
      }

      case "restart":
        resetGameState();
        setStatus("setting_up");

        setPlayers((prev) =>
          prev.map((p) => ({ ...p, score: 0 }))
        );

        setTeams((prev) =>
          prev.map((t) => ({ ...t, score: 0 }))
        );
        break;
    }
  }

  function sendGuess(data: GuessData) {
    socket?.send(data);
  }

  function sendSwitch(data: SwitchData) {
    socket?.send(data);
  }

  function sendAction(type: string) {
    socket?.send({ type });
  }

  function sendKick(playerId: string) {
    socket?.send({ type: "kick", id: playerId });
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
    hostId,
    currentPlayerId,
    guessedMap,
    logs,
    endTime,
    winners,
    isDraw,
    sendGuess,
    sendSwitch,
    sendAction,
    sendKick,
  };
}