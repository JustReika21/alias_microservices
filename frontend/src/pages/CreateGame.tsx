import { useState } from "react";
import { createGame } from "../services/gameService";

export default function CreateGame() {
  const [rounds, setRounds] = useState(5);
  const [time, setTime] = useState(10);
  const [pack, setPack] = useState(9);
  const [password, setPassword] = useState("");
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      await createGame({
        rounds,
        time,
        pack,
        password: password || null,
      });

      setResult("Game created!");
    } catch (e: any) {
      if (e.message === "Failed to fetch") {
        setResult("Session expired");
      } else {
        setResult("Error: " + e.message);
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={"panel default-box"}>
      <h2>Create Game</h2>

      <form onSubmit={handleSubmit} style={{ display: 'contents' }}>
        <input
          type="number"
          placeholder="Rounds"
          value={rounds}
          onChange={(e) => setRounds(Number(e.target.value))}
          required
        />
        <input
          type="number"
          placeholder="Time (seconds)"
          value={time}
          onChange={(e) => setTime(Number(e.target.value))}
          required
        />
        <input
          type="number"
          placeholder="Pack ID"
          value={pack}
          onChange={(e) => setPack(Number(e.target.value))}
          required
        />
        <input
          type="text"
          placeholder="Password (optional)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Creating..." : "Create Game"}
        </button>
      </form>

      {result && <div className="msg">{result}</div>}
    </div>
  );
}