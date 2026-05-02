export type GuessData = {
  type: "guessed" | "not_guessed";
  card: number;
};

export type SwitchData = {
  type: "switch_team";
  new_team_id: number
}