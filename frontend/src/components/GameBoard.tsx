import { useEffect, useRef, useState } from "react";
import { useGame } from "../hooks/useGame";
import { STATUS_CONFIG } from "../types/game_button";
import type { Status } from "../types/game_button";

import TeamGrid from "./TeamGrid";
import CardStack from "./CardStack";
import Timer from "./Timer";
import GameButton from "./GameButton";

export default function GameBoard({ gameId }: { gameId: string }) {
  const {
    players,
    teams,
    cards,
    status,
    isMyTurn,
    myId,
    currentPlayerId,
    guessedMap,
    logs,
    endTime,
    sendGuess,
    sendAction,
  } = useGame(gameId);

  const [disabled, setDisabled] = useState(false);
  const timeoutRef = useRef<number | null>(null);

  useEffect(() => {
    if (status !== "calculating") return;

    setDisabled(true);

    if (timeoutRef.current) clearTimeout(timeoutRef.current);

    timeoutRef.current = window.setTimeout(() => {
      setDisabled(false);
    }, 500);
  }, [status]);

  const handleAction = (action: string) => {
    const delay = STATUS_CONFIG[status as Status].clickDelay;

    setDisabled(true);

    if (timeoutRef.current) clearTimeout(timeoutRef.current);

    timeoutRef.current = window.setTimeout(() => {
      setDisabled(false);
    }, delay);

    sendAction(action);
  };

  return (
    <div>
      <TeamGrid
        players={players}
        teams={teams}
        status={status}
        myId={myId}
        currentPlayerId={currentPlayerId}
      />

      <Timer endTime={endTime} />

      <CardStack
        cards={cards}
        guessedMap={guessedMap}
        status={status}
        sendAction={sendGuess}
      />

      {isMyTurn && (
        <GameButton
          status={status}
          onAction={handleAction}
          disabled={disabled}
        />
      )}

      <div style={{ height: 200, overflowY: "auto" }}>
        {logs.map((l, i) => (
          <div key={i}>{l}</div>
        ))}
      </div>
    </div>
  );
}