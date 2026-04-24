interface CardStackProps {
  cards: any[];
  guessedMap: Record<number, boolean>;
  status: string;
  sendAction: (msg: any) => void;
}

export default function CardStack({
  cards,
  guessedMap,
  status,
  sendAction
}: CardStackProps) {
  return (
    <div>
      {cards.map(card => (
        <div key={card.id} className={`card-item ${guessedMap[card.id] ? "guessed" : ""}`}>
          {card.word}
          {status === "calculating" && (
            <div className="card-actions">
              <button onClick={() => sendAction({ type: "guessed", card: card.id })}>GUESSED</button>
              <button onClick={() => sendAction({ type: "not_guessed", card: card.id })}>NOT GUESSED</button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}