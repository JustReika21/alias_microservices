import {apiFetch} from "./api.ts";

export async function fetchCards(packId: number) {
  const res = await apiFetch(`/api/v1/cards?pack_id=${packId}`, {
    method: "GET"
  });

  if (!res.ok) throw new Error("Failed to fetch cards");
  return res.json();
}