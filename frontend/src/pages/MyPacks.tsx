import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { fetchMyPacks, type MyPacksResponse } from "../services/packService";

export default function MyPacks() {
  const navigate = useNavigate();

  const [data, setData] = useState<MyPacksResponse | null>(null);
  const [page, setPage] = useState(1);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load(p: number) {
    setLoading(true);

    try {
      const res = await fetchMyPacks(p);
      setData(res);
      setPage(res.page);
    } catch (e) {
      if (e instanceof Error) setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load(1);
  }, []);

  if (loading && !data) {
    return <div className="container">Loading...</div>;
  }

  if (error) {
    return <div className="container">{error}</div>;
  }

  if (!data) {
    return <div className="container">No data</div>;
  }

  return (
    <div className="container my-packs-page">
      <h1>My Packs</h1>

      {data.items.length === 0 && <p>No packs yet</p>}

      <div className="packs-list">
        {data.items.map((pack) => (
          <div
            key={pack.id}
            className="pack-card"
            onClick={() =>
              navigate(`/pack/edit/${pack.id}`)
            }
          >
            <div className="pack-name">{pack.name}</div>
            <div className="pack-meta">
              {pack.total} cards
            </div>
          </div>
        ))}
      </div>

      <div className="pagination">
        <button
          disabled={page <= 1}
          onClick={() => load(page - 1)}
        >
          Prev
        </button>

        <div className="page-info">
          Page {data.page} / {data.pages}
        </div>

        <button
          disabled={page >= data.pages}
          onClick={() => load(page + 1)}
        >
          Next
        </button>
      </div>
    </div>
  );
}
