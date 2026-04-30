export type Status = "setting_up" | "waiting" | "started" | "calculating";

export type ActionConfig = {
  label: string;
  action: string;
  clickDelay: number;
};

export const STATUS_CONFIG: Record<Status, ActionConfig> = {
  setting_up: { label: "Set Up", action: "set_up", clickDelay: 100 },
  waiting: { label: "Start", action: "start", clickDelay: 100 },
  started: { label: "Next", action: "next", clickDelay: 100 },
  calculating: { label: "Calculated", action: "calculated", clickDelay: 1000 },
};