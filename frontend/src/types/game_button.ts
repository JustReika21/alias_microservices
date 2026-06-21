export type Status =
  | "setting_up"
  | "waiting"
  | "started"
  | "calculating"
  | "finished";

export type ActionConfig = {
  label: string;
  action: string;
  clickDelay: number;
};

export const STATUS_CONFIG: Record<Status, ActionConfig> = {
  setting_up: {
    label: "Начать игру",
    action: "set_up",
    clickDelay: 100,
  },
  waiting: {
    label: "Старт",
    action: "start",
    clickDelay: 100,
  },
  started: {
    label: "Далее",
    action: "next",
    clickDelay: 100,
  },
  calculating: {
    label: "Подсчёт очков",
    action: "calculated",
    clickDelay: 1000,
  },
  finished: {
    label: "Новая игра",
    action: "restart",
    clickDelay: 100,
  },
};