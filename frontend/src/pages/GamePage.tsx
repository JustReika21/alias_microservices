import { useParams } from "react-router-dom";
import GameBoard from "../components/GameBoard";
import {useEffect} from "react";

export default function GamePage() {
  const { gameId } = useParams<{ gameId: string }>();

  useEffect(() => {
    if (gameId) {
      document.title = `Алиас - Игра ${gameId}`;
    }
  }, [gameId]);

  if (!gameId) return <p>Game ID not found</p>;

  return (
    <div>
      <GameBoard gameId={gameId} />
    </div>
  );
}