import { useEffect, useRef, useState } from "react";
import { useGame } from "../hooks/useGame";
import { STATUS_CONFIG } from "../types/game_button";
import type { Status } from "../types/game_button";

import TeamGrid from "./TeamGrid";
import CardStack from "./CardStack";
import Timer from "./Timer";
import GameButton from "./GameButton";

export default function GameBoard({
  gameId,
}: {
  gameId: string;
}) {
  const {
    players,
    teams,
    cards,
    status,
    isMyTurn,
    myId,
    hostId,
    currentPlayerId,
    guessedMap,
    endTime,
    winners,
    isDraw,
    sendGuess,
    sendSwitch,
    sendAction,
    sendKick,
  } = useGame(gameId);

  const [disabled, setDisabled] = useState(false);
  const timeoutRef = useRef<number | null>(null);

  const canUseActionButton =
    (status === "setting_up" &&
      String(myId) === String(hostId)) ||
    (status === "finished" &&
      String(myId) === String(hostId)) ||
    ((status === "waiting" ||
      status === "started" ||
      status === "calculating") &&
      isMyTurn);

  useEffect(() => {
    if (status !== "calculating") return;

    setDisabled(true);

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = window.setTimeout(() => {
      setDisabled(false);
    }, 500);
  }, [status]);

  const handleAction = (action: string) => {
    const delay =
      STATUS_CONFIG[status as Status].clickDelay;

    setDisabled(true);

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

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
        hostId={hostId}
        currentPlayerId={currentPlayerId}
        winners={winners}
        sendSwitch={sendSwitch}
        sendKick={sendKick}
      />

      {status === "finished" && (
        <div className="game-result">
          {isDraw
            ? "Ничья"
            : `Победила команда ${winners[0]}`}
        </div>
      )}

      <Timer endTime={endTime} />

      <CardStack
        cards={cards}
        guessedMap={guessedMap}
        status={status}
        sendAction={sendGuess}
      />

      {canUseActionButton && (
        <GameButton
          status={status as Status}
          onAction={handleAction}
          disabled={disabled}
        />
      )}
    </div>
  );
}