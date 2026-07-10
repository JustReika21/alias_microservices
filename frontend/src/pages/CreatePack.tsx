import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useToast } from "../components/ToastProvider";
import { createPack } from "../services/packService";

import { useEffect } from "react";

export default function CreatePack() {
  useEffect(() => {
    document.title = "Алиас - Создать пак";
  }, []);

  const { showToast } = useToast();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (loading) return;

    setLoading(true);

    const packData = {
      name: name.trim(),
      description: description.trim() || null,
    };

    try {
      const data = await createPack(packData);

      showToast("Пак успешно создан", "success");

      navigate(`/pack/edit/${data.id}`);
    } catch (err: any) {
      showToast(
        err.message || "Не удалось создать пак",
        "error"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel default-box">
      <h2>Создать пак</h2>

      <form onSubmit={handleSubmit} style={{ display: "contents" }}>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Название"
          required
          disabled={loading}
        />

        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Описание"
          disabled={loading}
        />

        <button type="submit" disabled={loading}>
          {loading ? "Создание..." : "Создать пак"}
        </button>
      </form>
    </div>
  );
}