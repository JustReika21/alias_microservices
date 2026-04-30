import { useEffect, useState } from "react";

interface TimerProps {
  endTime: number | null;
}

export default function Timer({ endTime }: TimerProps) {
  const [remaining, setRemaining] = useState<number>(0);

  useEffect(() => {
    if (!endTime) {
      setRemaining(0);
      return;
    }

    const updateRemaining = () => {
      const now = Date.now() / 1000;
      setRemaining(Math.max(0, endTime - now));
    };

    updateRemaining();
    const interval = setInterval(updateRemaining, 250);
    return () => clearInterval(interval);
  }, [endTime]);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60)
      .toString()
      .padStart(2, "0");
    const s = Math.floor(seconds % 60)
      .toString()
      .padStart(2, "0");
    return `${m}:${s}`;
  };

  return (
    <div style={{ textAlign: "center", margin: "10px 0", fontSize: "24px" }}>
      {formatTime(remaining)}
    </div>
  );
}