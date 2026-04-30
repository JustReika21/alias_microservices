import { STATUS_CONFIG } from "../types/game_button";
import type { Status } from "../types/game_button";

interface Props {
  status: Status;
  onAction: (action: string) => void;
  disabled: boolean;
}

export default function GameButton({ status, onAction, disabled }: Props) {
  const cfg = STATUS_CONFIG[status];
  if (!cfg) return null;

  return (
    <div className="action-container">
      <button
        className="action-button"
        disabled={disabled}
        onClick={() => onAction(cfg.action)}
      >
        {cfg.label}
      </button>
    </div>
  );
}