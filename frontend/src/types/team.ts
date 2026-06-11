export type Player = {
  id: string;
  name: string;
  score: number;
  teamId: string;
  connected?: boolean;
};

export interface Team {
  id: string;
  totalPlayers: number;
  score: number;
}

export interface Props {
  players?: Player[];
  teams?: Team[];
  status?: string;
}