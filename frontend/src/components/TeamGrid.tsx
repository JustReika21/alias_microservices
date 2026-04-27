// /components/TeamGrid.tsx
import { useMemo } from "react";
import type { Player, Team, Props } from "../types/team";

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
    acc[t.id] = t.score;
    return acc;
  }, {});
}

export default function TeamGrid({
  players = [],
  teams = [],
  status,
}: Props) {
  const playersByTeam = useMemo(
    () => groupPlayersByTeam(players),
    [players]
  );

  const teamScores = useMemo(
    () => buildTeamScores(teams),
    [teams]
  );

  const teamIds = useMemo(() => {
    if (status === "setting_up") {
      return DEFAULT_TEAM_IDS;
    }

    return DEFAULT_TEAM_IDS.filter(
      (id) => (playersByTeam[id] || []).length > 0
    );
  }, [playersByTeam, status]);

  return (
    <div className="team-grid">
      {teamIds.map((teamId) => {
        const teamPlayers = playersByTeam[teamId] || [];
        const teamScore = teamScores[teamId] ?? 0;

        return (
          <div key={teamId} className="team-box">
            <div className="team-title">
              T{teamId} - {teamScore} pts
            </div>

            <div className="team-players">
              {teamPlayers.length === 0 ? (
                <div className="empty">—</div>
              ) : (
                teamPlayers.map((p) => (
                  <div key={p.id} className="player">
                    <div className="player-name">{p.name}</div>
                    <div className="player-score">
                      {p.score} pts
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}