import { apiFetch } from "./api";

import type { Pack } from "../types/pack";

export async function createPack(payload: {
  name: string;
  description?: string | null;
}): Promise<Pack> {
  const res = await apiFetch("/api/v1/packs", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Failed to create pack");
  }

  return res.json();
}

export async function fetchPack(
  packId: number
): Promise<Pack> {
  const res = await apiFetch(
    `/api/v1/packs/edit/${packId}`
  );

  if (res.status === 403) {
    throw new Error("Forbidden");
  }

  if (res.status === 404) {
    throw new Error("Pack not found");
  }

  if (!res.ok) {
    throw new Error("Failed to fetch pack");
  }

  return res.json();
}

export async function updatePack(
  packId: number,
  payload: {
    name: string;
    description?: string | null;
  }
): Promise<Pack> {
  const res = await apiFetch(
    `/api/v1/packs/${packId}`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    }
  );

  if (!res.ok) {
    throw new Error("Failed to update pack");
  }

  return res.json();
}

export async function deletePack(
  packId: number
): Promise<void> {
  const res = await apiFetch(
    `/api/v1/packs/${packId}`,
    {
      method: "DELETE",
    }
  );

  if (!res.ok) {
    throw new Error("Failed to delete pack");
  }
}

export type PackPreview = {
  id: number;
  name: string;
  total: number;
};

export type PacksResponse = {
  items: PackPreview[];
  total: number;
  page: number;
  limit: number;
  pages: number;
};

export async function fetchMyPacks(page = 1): Promise<PacksResponse> {
  const res = await apiFetch(`/api/v1/packs/my?page=${page}`);

  if (!res.ok) {
    throw new Error("Failed to fetch packs");
  }

  return res.json();
}

let nextRequestTime = 0;

export async function fetchPacksByName(
  packName: string,
  page = 1
): Promise<PacksResponse> {
  if (Date.now() < nextRequestTime) {
    throw new Error("Server temporarily unavailable");
  }

  const params = new URLSearchParams();

  if (packName.trim()) {
    params.append("pack_name", packName);
  }

  params.append("page", page.toString());

  try {
    const res = await apiFetch(`/api/v1/packs?${params}`);

    if (!res.ok) {
      if (res.status >= 500) {
        nextRequestTime = Date.now() + 3000;
      }

      throw new Error("Failed to fetch packs");
    }

    nextRequestTime = 0;

    return await res.json();
  } catch (err) {
    nextRequestTime = Date.now() + 3000;
    throw err;
  }
}