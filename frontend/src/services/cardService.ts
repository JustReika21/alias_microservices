import { apiFetch } from "./api";

import type { Card } from "../types/card";

export async function fetchCards(
  packId: number
): Promise<Card[]> {
  const res = await apiFetch(
    `/api/v1/cards?pack_id=${packId}`
  );

  if (!res.ok) {
    throw new Error("Failed to fetch cards");
  }

  return res.json();
}

export async function createCards(
  packId: number,
  words: string[]
): Promise<void> {
  const res = await apiFetch("/api/v1/cards", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      pack_id: packId,
      words,
    }),
  });

  if (!res.ok) {
    throw new Error("Failed to create cards");
  }
}

export async function deleteCards(
  packId: number,
  cardIds: number[]
): Promise<void> {
  const res = await apiFetch("/api/v1/cards", {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      pack_id: packId,
      card_ids: cardIds,
    }),
  });

  if (!res.ok) {
    throw new Error("Failed to delete cards");
  }
}
