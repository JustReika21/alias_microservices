import { useParams } from "react-router-dom";
import GameBoard from "../components/GameBoard";

export default function GamePage() {
  const { gameId } = useParams<{ gameId: string }>();

  if (!gameId) return <p>Game ID not found</p>;

  return (
    <div>
      <h1>Game Room: {gameId}</h1>
      <GameBoard gameId={gameId} />
    </div>
  );
}