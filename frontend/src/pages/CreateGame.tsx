import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { fetchPacksByName } from "../services/packService";
import { fetchCards } from "../services/cardService";
import { createGame } from "../services/gameService";

import { useToast } from "../components/ToastProvider";

export default function CreateGame() {
  const navigate = useNavigate();
  const loaderRef = useRef<HTMLDivElement>(null);

  const [packs, setPacks] = useState<any[]>([]);
  const [cards, setCards] = useState<any[]>([]);
  const [selectedPack, setSelectedPack] = useState<number | null>(null);

  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const [rounds, setRounds] = useState("5");
  const [time, setTime] = useState("60");

  const [password, setPassword] = useState("");

  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  const [loading, setLoading] = useState(false);
  const [packsLoading, setPacksLoading] = useState(false);

  const { showToast } = useToast();

  useEffect(() => {
    document.title = "Алиас - Создать игру";
  }, []);

  async function loadPacks(
    p: number,
    query: string,
    replace = false
  ) {
    if (packsLoading || (!hasMore && !replace)) return;

    setPacksLoading(true);

    try {
      const res = await fetchPacksByName(query, p);

      setPacks((prev) =>
        replace ? res.items : [...prev, ...res.items]
      );

      setPage(p);

      setHasMore(res.items.length > 0);

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

    if (!selectedPack || loading) return;

    const roundsValue = Number(rounds);
    const timeValue = Number(time);

    if (!roundsValue || roundsValue < 1) {
      showToast("Количество раундов должно быть больше 0", "error");
      return;
    }

    if (!roundsValue || roundsValue > 50) {
      showToast("Количество раундов должно меньше 50", "error");
      return;
    }

    if (!timeValue || timeValue < 30) {
      showToast("Время должно быть больше 30 секунд", "error");
      return;
    }

    if (!timeValue || timeValue > 600) {
      showToast("Время должно быть больше 600 секунд", "error");
      return;
    }

    setLoading(true);

    try {
      const game = await createGame({
        rounds: roundsValue,
        time: timeValue,
        pack: selectedPack,
        password: password || null,
      });

      showToast("Игра успешно создана", "success");

      navigate(`/game/${game.id}`);
    } catch (e: any) {
      showToast(e.message, "error");
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
          loadPacks(
            page + 1,
            debouncedSearch,
            false
          );
        }
      },
      {
        root: document.querySelector(".packs-list"),
        threshold: 0.8,
      }
    );

    observer.observe(loader);

    return () => observer.disconnect();
  }, [
    page,
    packsLoading,
    hasMore,
    debouncedSearch,
  ]);

  return (
    <div className="create-game-layout">
      <div className="create-game-window">
        <div className="create-game-header">
          <h2>Пользовательские паки</h2>

          <div className="create-game-info">
            <span>Карт: {cards.length}</span>
          </div>
        </div>

        <div className="create-game-content">
          <div className="packs-panel">
            <div className="packs-search">
              <input
                value={search}
                onChange={(e) =>
                  setSearch(e.target.value)
                }
                placeholder="Поиск набора..."
              />
            </div>

            <div className="packs-list">
              {packs.map((p) => (
                <div
                  key={p.id}
                  className={`pack-item ${
                    selectedPack === p.id
                      ? "active"
                      : ""
                  }`}
                  onClick={() =>
                    selectPack(p.id)
                  }
                >
                  {p.name}
                </div>
              ))}

              <div
                ref={loaderRef}
                className="packs-loader"
              >
                {packsLoading && "Загрузка..."}
              </div>
            </div>
          </div>

          <div className="cards-panel">
            <div className="cards-list">
              {cards.map((c) => (
                <div
                  key={c.id}
                  className="card-chip"
                >
                  {c.word}
                </div>
              ))}
            </div>

            <form
              onSubmit={handleSubmit}
              className="game-form"
            >
              <div className="game-field">
                <label htmlFor="rounds">
                  Раунды
                </label>

                <input
                  id="rounds"
                  type="number"
                  min="1"
                  inputMode="numeric"
                  value={rounds}
                  onChange={(e) => {
                    const value =
                      e.target.value;

                    if (
                      value === "" ||
                      Number(value) >= 1
                    ) {
                      setRounds(value);
                    }
                  }}
                />
              </div>

              <div className="game-field">
                <label htmlFor="time">
                  Время (сек)
                </label>

                <input
                  id="time"
                  type="number"
                  min="1"
                  inputMode="numeric"
                  value={time}
                  onChange={(e) => {
                    const value =
                      e.target.value;

                    if (
                      value === "" ||
                      Number(value) >= 1
                    ) {
                      setTime(value);
                    }
                  }}
                />
              </div>

              <div className="game-field game-field-password">

                <label htmlFor="password">
                  Пароль
                  <span className="field-status">
                    {" "}
                  </span>
                </label>

                <input
                  id="password"
                  type="text"
                  value={password}
                  placeholder="(Скоро)"
                  disabled
                  onChange={(e) =>
                    setPassword(e.target.value)
                  }
                />
              </div>

              <button
                type="submit"
                disabled={
                  !selectedPack ||
                  loading
                }
              >
                {loading
                  ? "Создание..."
                  : "Создать"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}