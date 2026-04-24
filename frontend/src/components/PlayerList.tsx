interface PlayerListProps {
  players?: any[];
}

export default function PlayerList({ players = [] }: PlayerListProps) {
  if (!players.length) return <div>Players: empty</div>;
  return (
    <div>
      {players.map(p => (
        <span key={p.id}>{p.name} ({p.score})</span>
      ))}
    </div>
  );
}