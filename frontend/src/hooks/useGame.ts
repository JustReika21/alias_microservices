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
    const entry =
      `[${new Date().toLocaleTimeString()}] ${msg}` +
      (data ? ` ${JSON.stringify(data)}` : "");

    setLogs((prev) => [...prev, entry]);
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

    if (snapshot.my_id !== undefined) {
      setMyId(String(snapshot.my_id));
    }

    if (snapshot.host !== undefined) {
      setHostId(String(snapshot.host));
    }

    if (snapshot.current_player?.player_id !== undefined) {
      setCurrentPlayerId(String(snapshot.current_player.player_id));
    }

    if (snapshot.players) {
      setPlayers(snapshot.players.map(normalizePlayer));
    }

    if (snapshot.teams) {
      setTeams(snapshot.teams.map(normalizeTeam));
    }

    if (snapshot.cards) {
      setCards(snapshot.cards);
    }

    if (snapshot.end_time) {
      setEndTime(snapshot.end_time);
    }

    if (snapshot.status === "calculating" && snapshot.cards) {
      const map: Record<number, boolean> = {};

      snapshot.cards.forEach((c: any) => {
        map[c.id] = true;
      });

      setGuessedMap(map);
    }

    if (
      snapshot.status === "finished" &&
      snapshot.winners
    ) {
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

      case "player_joined":
        if (data.player) {
          const newPlayer = normalizePlayer(data.player);

          setPlayers((prev) => {
            const exists = prev.some(
              (p) => p.id === newPlayer.id
            );

            if (exists) return prev;

            return [...prev, newPlayer];
          });
        }
        break;

      case "player_switch_team":
        setPlayers((prev) => {
          const player = prev.find(
            (p) => p.id === String(data.player_id)
          );

          if (!player) return prev;

          const withoutPlayer = prev.filter(
            (p) => p.id !== String(data.player_id)
          );

          const movedPlayer = {
            ...player,
            teamId: String(data.new_team_id),
          };

          return [...withoutPlayer, movedPlayer];
        });

        if (data.current_player_id !== undefined) {
          setCurrentPlayerId(String(data.current_player_id));
        }

        if (data.current_player_id !== undefined) {
          setCurrentPlayerId(
            String(data.current_player_id)
          );
        }
        break;

      case "players":
        setPlayers(
          (data.players || []).map(normalizePlayer)
        );
        break;

      case "teams":
        setTeams(
          (data.teams || []).map(normalizeTeam)
        );
        break;

      case "team_score_update":
        setTeams((prev) =>
          prev.map((t) =>
            t.id === String(data.id)
              ? {
                  ...t,
                  score: Number(data.score),
                }
              : t
          )
        );
        break;

      case "player_score_update":
        setPlayers((prev) =>
          prev.map((p) =>
            p.id === String(data.id)
              ? {
                  ...p,
                  score: Number(data.score),
                }
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
          data.value === "setting_up" ||
          data.value === "waiting" ||
          data.value === "started"
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
        const winnerIds = (data.winners || []).map(
          String
        );

        setStatus("finished");
        setWinners(winnerIds);
        setIsDraw(winnerIds.length > 1);

        break;
      }

      case "restart":
        resetGameState();

        setStatus("setting_up");

        setPlayers((prev) =>
          prev.map((p) => ({
            ...p,
            score: 0,
          }))
        );

        setTeams((prev) =>
          prev.map((t) => ({
            ...t,
            score: 0,
          }))
        );

        break;
    }
  }

  function sendGuess(guessData: GuessData) {
    socket?.send(guessData);
    log("send guess", guessData);
  }

  function sendSwitch(data: SwitchData) {
    socket?.send(data);
    log("send switch", data);
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
  };
}
