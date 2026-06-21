import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createPack } from "../services/packService";

export default function CreatePack() {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [msg, setMsg] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg("Загрузка...");

    const packData = {
      name: name.trim(),
      description: description.trim() || null,
    };

    try {
      const data = await createPack(packData);
      navigate(`/pack/edit/${data.id}`);
    } catch (err: any) {
      setMsg("Ошибка: " + (err.message || "Сессия истекла"));
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
        />

        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Описание"
        />

        <button type="submit">Создать пак</button>

        <div>{msg}</div>
      </form>
    </div>
  );
}