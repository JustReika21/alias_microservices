export type GameMessage =
  | { type: "set_up" }
  | { type: "start" }
  | { type: "next" }
  | { type: "calculated" }
  | { type: "guess"; card: number; guessed: boolean };

export type GuessData = {
  type: "guessed" | "not_guessed";
  card: number;
};