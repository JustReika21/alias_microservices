import { useGame } from "../hooks/useGame";
import PlayerList from "./PlayerList";
import CardStack from "./CardStack";

export default function GameBoard({ gameId }: { gameId: string }) {
  const {
    players,
    cards,
    status,
    currentPlayer,
    guessedMap,
    logs,
    sendGuess,
    sendAction
  } = useGame(gameId);

  return (
    <div>
      <PlayerList players={players} />

      <CardStack
        cards={cards}
        guessedMap={guessedMap}
        status={status}
        sendAction={sendGuess}
      />

      {currentPlayer && (
        <div>
          {status === "setting_up" && (
            <button onClick={() => sendAction("set_up")}>Set Up</button>
          )}

          {status === "waiting" && (
            <button onClick={() => sendAction("start")}>Start</button>
          )}

          {status === "started" && (
            <button onClick={() => sendAction("next")}>Next</button>
          )}

          {status === "calculating" && (
            <button onClick={() => sendAction("calculated")}>Calculated</button>
          )}
        </div>
      )}

      <div style={{ height: 200, overflowY: "auto" }}>
        {logs.map((l, i) => <div key={i}>{l}</div>)}
      </div>
    </div>
  );
}