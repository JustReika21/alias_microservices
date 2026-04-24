import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createPack } from "../services/packService";

export default function CreatePack() {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [msg, setMsg] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setMsg("Loading...");

    const packData = { name: name.trim(), description: description.trim() || null };

    try {
      const data = await createPack(packData);
      navigate(`/pack/edit/${data.id}`);
    } catch (err: any) {
      setMsg("Error: " + err.message || "Session expired");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Name"
        required
      />
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description"
      />
      <button type="submit">Create Pack</button>
      <div>{msg}</div>
    </form>
  );
}