import { useMemo, useState } from "react";
import type { Player, Team } from "../types/team";
import type { SwitchData } from "../types/game";

type Props = {
  players: Player[];
  teams: Team[];
  status: string;
  myId?: string | null;
  hostId?: string | null;
  currentPlayerId?: string | null;
  winners?: string[];
  sendSwitch: (data: SwitchData) => void;
  sendKick: (playerId: string) => void;
};

const DEFAULT_TEAM_IDS = ["1", "2", "3", "4"];

function groupPlayersByTeam(players: Player[]) {
  return players.reduce<Record<string, Player[]>>((acc, p) => {
    const key = (p as any).teamId;
    if (!acc[key]) acc[key] = [];
    acc[key].push(p);
    return acc;
  }, {});
}

function buildTeamScores(teams: Team[]) {
  return teams.reduce<Record<string, number>>((acc, t) => {
    acc[t.id] = Number(t.score);
    return acc;
  }, {});
}

export default function TeamGrid({
  players = [],
  teams = [],
  status,
  myId,
  hostId,
  currentPlayerId,
  winners = [],
  sendSwitch,
  sendKick,
}: Props) {
  const [hoveredPlayer, setHoveredPlayer] = useState<string | null>(null);

  const normalizedPlayers = useMemo(() => {
    return players.map((p: any) => ({
      ...p,
      teamId: p.teamId ?? p.team_id,
      score: Number(p.score),
      connected: p.connected ?? true,
    }));
  }, [players]);

  const playersByTeam = useMemo(
    () => groupPlayersByTeam(normalizedPlayers),
    [normalizedPlayers]
  );

  const teamScores = useMemo(() => buildTeamScores(teams), [teams]);

  const myTeamId = useMemo(() => {
    const me = normalizedPlayers.find(
      (p) => String(p.id) === String(myId)
    );
    return me ? String(me.teamId) : null;
  }, [normalizedPlayers, myId]);

  const isHost = String(hostId) === String(myId);

  const teamIds = useMemo(() => {
    if (status === "setting_up") return DEFAULT_TEAM_IDS;

    return DEFAULT_TEAM_IDS.filter(
      (id) => (playersByTeam[id] || []).length > 0
    );
  }, [playersByTeam, status]);

  function handleKick(playerId: string) {
    const player = normalizedPlayers.find(
      (p) => String(p.id) === String(playerId)
    );

    const name = player?.name ?? "игрок";

    if (!window.confirm(`Исключить игрока: ${name}?`)) return;

    sendKick(playerId);
  }

  return (
    <div className="team-grid">
      {teamIds.map((teamId) => {
        const teamPlayers = playersByTeam[teamId] || [];
        const teamScore = teamScores[teamId] ?? 0;

        const isMyTeam = teamPlayers.some(
          (p) => String(p.id) === String(myId)
        );

        const isWinner =
          status === "finished" &&
          winners.includes(String(teamId));

        return (
          <div
            key={teamId}
            className={`team-box ${isWinner ? "winner" : ""}`}
          >
            <div className="team-title">
              T{teamId} - {teamScore}
            </div>

            <div className="team-players">
              {teamPlayers.length === 0 && (
                <div className="empty">—</div>
              )}

              {teamPlayers.map((p) => {
                const isMe = String(p.id) === String(myId);
                const isTurn = String(p.id) === String(currentPlayerId);
                const isHostPlayer = String(p.id) === String(hostId);
                const isOffline = !p.connected;
                const canKick = isHost && !isMe;

                return (
                  <div
                    key={p.id}
                    className={`player ${isTurn ? "turn" : ""}`}
                    onMouseEnter={() => setHoveredPlayer(String(p.id))}
                    onMouseLeave={() => setHoveredPlayer(null)}
                  >
                    <div className="player-name">
                      {isHostPlayer && (
                        <span
                          className={`host-icon ${
                            isOffline ? "offline" : ""
                          }`}
                        >
                          ♔
                        </span>
                      )}

                      {isMe && <span className="me-tag">(Вы)</span>}

                      <span
                        className={`name-text ${
                          isOffline ? "offline" : ""
                        }`}
                      >
                        {p.name}
                      </span>
                    </div>

                    <div className="player-right">
                      {canKick &&
                      hoveredPlayer === String(p.id) ? (
                        <button
                          className="kick-btn"
                          onClick={() => handleKick(String(p.id))}
                        >
                          ✕
                        </button>
                      ) : (
                        <span
                          className={`player-score ${
                            isOffline ? "offline" : ""
                          }`}
                        >
                          {p.score}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {status === "setting_up" && myTeamId && !isMyTeam && (
              <button
                className="join-btn"
                onClick={() =>
                  sendSwitch({
                    type: "switch_team",
                    new_team_id: Number(teamId),
                  })
                }
              >
                +
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}