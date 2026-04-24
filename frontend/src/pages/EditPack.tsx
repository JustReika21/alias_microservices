import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchPack, updatePack } from "../services/packService";
import { fetchCards } from "../services/cardService";

export default function EditPack() {
  const { packId } = useParams<{ packId: string }>();
  const [pack, setPack] = useState<{ name: string; description: string } | null>(null);
  const [cards, setCards] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      if (!packId) {
        setError("Pack ID not found");
        setLoading(false);
        return;
      }
      try {
        const packData = await fetchPack(Number(packId));
        setPack(packData);

        const cardsData = await fetchCards(Number(packId));
        setCards(cardsData);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [packId]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!pack) return;

    try {
      await updatePack(Number(packId), pack.name, pack.description || "");
      alert("Pack updated successfully");
    } catch (e: any) {
      alert("Error updating pack: " + e.message);
    }
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h2>Edit Pack</h2>
      <form onSubmit={handleSubmit}>
        <input
          value={pack!.name}
          onChange={(e) => setPack({ ...pack!, name: e.target.value })}
          placeholder="Pack name"
          required
        />
        <textarea
          value={pack!.description || ""}
          onChange={(e) => setPack({ ...pack!, description: e.target.value })}
          placeholder="Pack description"
        />
        <button type="submit">Update Pack</button>
      </form>

      <ul>
        {cards.map((card) => (
          <li key={card.id}>{card.word}</li>
        ))}
      </ul>
    </div>
  );
}