import { useMemo } from "react";
import type { Player, Team } from "../types/team";
import type { SwitchData } from "../types/game";

type Props = {
  players: Player[];
  teams: Team[];
  status: string;
  myId?: string | null;
  hostId?: string | null;
  currentPlayerId?: string | null;
  sendSwitch: (data: SwitchData) => void;
};

const DEFAULT_TEAM_IDS = ["1", "2", "3", "4"];

function groupPlayersByTeam(players: Player[]): Record<string, Player[]> {
  return players.reduce<Record<string, Player[]>>((acc, p) => {
    if (!acc[p.teamId]) acc[p.teamId] = [];
    acc[p.teamId].push(p);
    return acc;
  }, {});
}

function buildTeamScores(teams: Team[]): Record<string, number> {
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
  sendSwitch,
}: Props) {
  const normalizedPlayers = useMemo(() => {
    return players.map((p: any) => ({
      ...p,
      teamId: p.teamId ?? p.team_id,
      score: Number(p.score),
    }));
  }, [players]);

  const playersByTeam = useMemo(
    () => groupPlayersByTeam(normalizedPlayers),
    [normalizedPlayers]
  );

  const teamScores = useMemo(
    () => buildTeamScores(teams),
    [teams]
  );

  const myTeamId = useMemo(() => {
    const me = normalizedPlayers.find(
      (p) => String(p.id) === String(myId)
    );
    return me ? String(me.teamId) : null;
  }, [normalizedPlayers, myId]);

  const teamIds = useMemo(() => {
    if (status === "setting_up") return DEFAULT_TEAM_IDS;

    return DEFAULT_TEAM_IDS.filter(
      (id) => (playersByTeam[id] || []).length > 0
    );
  }, [playersByTeam, status]);

  return (
    <div className="team-grid">
      {teamIds.map((teamId) => {
        const teamPlayers = playersByTeam[teamId] || [];
        const teamScore = teamScores[teamId] ?? 0;

        const isMyTeam = myTeamId === teamId;

        return (
          <div key={teamId} className="team-box">
            <div className="team-title">
              T{teamId} - {teamScore} pts
            </div>

            <div className="team-players">
              {teamPlayers.length === 0 ? (
                <div className="empty">—</div>
              ) : (
                teamPlayers.map((p) => {
                  const isMe = String(p.id) === String(myId);
                  const isTurn =
                    String(p.id) === String(currentPlayerId);
                  const isHost =
                    String(p.id) === String(hostId);

                  return (
                    <div
                      key={p.id}
                      className={`player ${isMe ? "me" : ""} ${
                        isTurn ? "turn" : ""
                      }`}
                    >
                      <div className="player-name">
                        {isHost && (
                          <span className="host-icon">♔</span>
                        )}
                        <span className="name-text">{p.name}</span>
                      </div>

                      <div className="player-score">
                        {p.score} pts
                      </div>
                    </div>
                  );
                })
              )}
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