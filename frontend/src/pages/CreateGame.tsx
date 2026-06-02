import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { fetchPacksByName } from "../services/packService";
import { fetchCards } from "../services/cardService";
import { createGame } from "../services/gameService";

export default function CreateGame() {
  const navigate = useNavigate();
  const loaderRef = useRef<HTMLDivElement>(null);

  const [packs, setPacks] = useState<any[]>([]);
  const [cards, setCards] = useState<any[]>([]);
  const [selectedPack, setSelectedPack] = useState<number | null>(null);

  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const [rounds, setRounds] = useState(5);
  const [time, setTime] = useState(10);
  const [password, setPassword] = useState("");

  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  const [loading, setLoading] = useState(false);
  const [packsLoading, setPacksLoading] = useState(false);

  async function loadPacks(p: number, query: string, replace = false) {
    if (packsLoading || (!hasMore && !replace)) return;

    setPacksLoading(true);

    try {
      const res = await fetchPacksByName(query, p);

      setPacks(prev =>
        replace ? res.items : [...prev, ...res.items]
      );

      setPage(p);

      if (res.items.length === 0) {
        setHasMore(false);
      } else {
        setHasMore(true);
      }

      if (replace && res.items.length > 0 && !selectedPack) {
        selectPack(res.items[0].id);
      }
    } finally {
      setPacksLoading(false);
    }
  }

  async function selectPack(id: number) {
    setSelectedPack(id);
    const cards = await fetchCards(id);
    setCards(cards);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedPack) return;

    setLoading(true);

    try {
      const game = await createGame({
        rounds,
        time,
        pack: selectedPack,
        password: password || null,
      });

      navigate(`/game/${game.id}`);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const t = setTimeout(() => {
      setDebouncedSearch(search.trim());
    }, 400);

    return () => clearTimeout(t);
  }, [search]);

  useEffect(() => {
    setPacks([]);
    setPage(1);
    setHasMore(true);
    setSelectedPack(null);
    setCards([]);

    loadPacks(1, debouncedSearch, true);
  }, [debouncedSearch]);

  useEffect(() => {
    const loader = loaderRef.current;
    if (!loader) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (
          entry.isIntersecting &&
          !packsLoading &&
          hasMore
        ) {
          loadPacks(page + 1, debouncedSearch, false);
        }
      },
      {
        root: document.querySelector(".packs-list"),
        threshold: 0.8,
      }
    );

    observer.observe(loader);

    return () => observer.disconnect();
  }, [page, packsLoading, hasMore, debouncedSearch]);

  return (
    <div className="create-game-layout">
      <div className="create-game-window">
        <div className="create-game-header">
          <h2>Custom word packs</h2>
          <div className="create-game-info">
            <span>Words {cards.length}</span>
          </div>
        </div>

        <div className="create-game-content">
          <div className="packs-panel">
            <div className="packs-search">
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search pack..."
              />
            </div>

            <div className="packs-list">
              {packs.map(p => (
                <div
                  key={p.id}
                  className={`pack-item ${
                    selectedPack === p.id ? "active" : ""
                  }`}
                  onClick={() => selectPack(p.id)}
                >
                  {p.name}
                </div>
              ))}

              <div ref={loaderRef} className="packs-loader">
                {packsLoading && "Loading..."}
              </div>
            </div>
          </div>

          <div className="cards-panel">
            <div className="cards-list">
              {cards.map(c => (
                <div key={c.id} className="card-chip">
                  {c.word}
                </div>
              ))}
            </div>

            <form onSubmit={handleSubmit} className="game-form">
              <input
                type="number"
                value={rounds}
                onChange={(e) => setRounds(Number(e.target.value))}
              />
              <input
                type="number"
                value={time}
                onChange={(e) => setTime(Number(e.target.value))}
              />
              <input
                type="text"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button disabled={!selectedPack || loading}>
                {loading ? "Creating..." : "Create"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}