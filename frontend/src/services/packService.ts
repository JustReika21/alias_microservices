import { apiFetch } from "./api";

export async function createPack(packData: { name: string; description?: string | null }) {
  const res = await apiFetch("/api/v1/packs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(packData),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text);
  }

  return res.json();
}

export async function fetchPack(packId: number) {
  const res = await apiFetch(`/api/v1/packs/edit/${packId}`);
  if (res.status === 403) throw new Error("Forbidden");
  if (res.status === 404) throw new Error("Not Found");
  if (!res.ok) throw new Error("Failed to fetch pack");

  return res.json();
}

export async function updatePack(packId: number, name: string, description?: string | null) {
  const res = await apiFetch(`/api/v1/packs/${packId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, description }),
  });

  if (!res.ok) throw new Error("Failed to update pack");
  return res.json();
}
