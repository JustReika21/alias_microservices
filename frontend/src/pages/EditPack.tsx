import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  deletePack,
  fetchPack,
  updatePack,
} from "../services/packService";

import {
  createCards,
  deleteCards,
  fetchCards,
} from "../services/cardService";

import type { Pack } from "../types/pack";

type UICard = {
  id: number | string;
  word: string;
  isNew?: boolean;
};

function generateId() {
  return `new-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export default function EditPack() {
  const navigate = useNavigate();
  const { packId } = useParams<{ packId: string }>();

  if (!packId) return <div className="container">Invalid pack ID</div>;
  const numericPackId = Number(packId);

  const [pack, setPack] = useState<Pack | null>(null);
  const [cards, setCards] = useState<UICard[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [selectedCards, setSelectedCards] = useState<Set<number>>(new Set());

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function load() {
      const [packData, cardsData] = await Promise.all([
        fetchPack(numericPackId),
        fetchCards(numericPackId),
      ]);

      setPack(packData);
      setCards(cardsData);
      setLoading(false);
    }

    load();
  }, [numericPackId]);

  function addWord(word: string) {
    const trimmed = word.trim();
    if (!trimmed) return;

    setCards((prev) => {
      const exists = prev.some(
        (c) => c.word.toLowerCase() === trimmed.toLowerCase()
      );
      if (exists) return prev;

      return [
        ...prev,
        { id: generateId(), word: trimmed, isNew: true },
      ];
    });
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addWord(inputValue);
      setInputValue("");
    }
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const value = e.target.value;

    if (value.includes(",")) {
      const parts = value.split(",");
      parts.slice(0, -1).forEach(addWord);
      setInputValue(parts[parts.length - 1]);
    } else {
      setInputValue(value);
    }
  }

  function handlePaste(e: React.ClipboardEvent<HTMLInputElement>) {
    e.preventDefault();

    const text = e.clipboardData.getData("text");

    const words = text
      .split(/[\n,]/)
      .map((w) => w.trim())
      .filter(Boolean);

    setCards((prev) => {
      const existing = new Set(prev.map((c) => c.word.toLowerCase()));

      const newCards = words
        .filter((w) => !existing.has(w.toLowerCase()))
        .map((w) => ({
          id: generateId(),
          word: w,
          isNew: true,
        }));

      return [...prev, ...newCards];
    });
  }

  function removeNewCard(id: number | string) {
    setCards((prev) => prev.filter((c) => c.id !== id));
  }

  function toggleCardSelect(id: number) {
    const newSet = new Set(selectedCards);
    newSet.has(id) ? newSet.delete(id) : newSet.add(id);
    setSelectedCards(newSet);
  }

  async function handleAdd() {
    const words = cards
      .filter((c) => c.isNew)
      .map((c) => c.word);

    if (!words.length) return;

    setSaving(true);
    try {
      await createCards(numericPackId, words);
      const fresh = await fetchCards(numericPackId);
      setCards(fresh);
      setInputValue("");
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteSelected() {
    if (selectedCards.size === 0) return;

    setSaving(true);
    try {
      await deleteCards(numericPackId, Array.from(selectedCards));
      const fresh = await fetchCards(numericPackId);
      setCards(fresh);
      setSelectedCards(new Set());
    } finally {
      setSaving(false);
    }
  }

  async function handleSavePack() {
    if (!pack) return;

    setSaving(true);
    try {
      await updatePack(numericPackId, {
        name: pack.name,
        description: pack.description || "",
      });
    } finally {
      setSaving(false);
    }
  }

  async function handleDeletePack() {
    if (!confirm("Delete this pack?")) return;
    await deletePack(numericPackId);
    navigate("/");
  }

  if (loading) return <div className="container">Loading...</div>;
  if (!pack) return <div className="container">Error</div>;

  return (
    <div className="container edit-pack-page">
      <div className="card">
        <h2>Edit Pack</h2>

        <div className="form-group">
          <label>Name</label>
          <input
            value={pack.name}
            onChange={(e) =>
              setPack({ ...pack, name: e.target.value })
            }
          />
        </div>

        <div className="form-group">
          <label>Description</label>
          <textarea
            rows={3}
            value={pack.description || ""}
            onChange={(e) =>
              setPack({
                ...pack,
                description: e.target.value,
              })
            }
          />
        </div>

        <div className="actions">
          <button onClick={handleSavePack} disabled={saving}>
            Save
          </button>

          <button
            className="danger-btn"
            onClick={handleDeletePack}
          >
            Delete Pack
          </button>
        </div>
      </div>

      <div className="panel cards-panel">
        <div className="cards-header">
          <h3>Cards ({cards.length})</h3>
        </div>

        <div className="tags-input">
          {cards.map((card) => (
            <div
              key={card.id}
              className={`card-tag ${
                typeof card.id === "number" &&
                selectedCards.has(card.id)
                  ? "selected"
                  : ""
              }`}
              onClick={() =>
                typeof card.id === "number" &&
                toggleCardSelect(card.id)
              }
            >
              {card.word}

              {card.isNew && (
                <span
                  className="remove"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeNewCard(card.id);
                  }}
                >
                  ✕
                </span>
              )}
            </div>
          ))}

          <input
            value={inputValue}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            onPaste={handlePaste}
            placeholder="Type word, press Enter or comma"
          />
        </div>

        <div className="actions">
          <button onClick={handleAdd} disabled={saving}>
            Add
          </button>

          <button
            className="danger-btn"
            onClick={handleDeleteSelected}
            disabled={selectedCards.size === 0 || saving}
          >
            Delete Selected ({selectedCards.size})
          </button>
        </div>
      </div>
    </div>
  );
}
