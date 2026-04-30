import { useParams } from "react-router-dom";
import GameBoard from "../components/GameBoard";

export default function GamePage() {
  const { gameId } = useParams<{ gameId: string }>();

  if (!gameId) return <p>Game ID not found</p>;

  return (
    <div>
      <GameBoard gameId={gameId} />
    </div>
  );
}