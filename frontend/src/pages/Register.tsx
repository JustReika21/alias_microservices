import {useEffect, useState} from "react";
import { useNavigate } from "react-router-dom";

import { registerUser } from "../services/authService";
import { useToast } from "../components/ToastProvider";

export default function Register() {
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const { showToast } = useToast();

  useEffect(() => {
    document.title = "Алиас - Регистрация";
  }, []);

  const handleRegister = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    if (loading) return;

    setLoading(true);

    try {
      await registerUser(
        name,
        password
      );

      showToast(
        "Регистрация успешна",
        "success"
      );

      navigate("/login");

    } catch (err: any) {

      showToast(
        err.message ||
        "Не удалось зарегистрироваться",
        "error"
      );

    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="panel default-box">
      <h2>Регистрация</h2>

      <form
        onSubmit={handleRegister}
        style={{ display: "contents" }}
      >
        <input
          value={name}
          onChange={(e) =>
            setName(e.target.value)
          }
          placeholder="Имя"
          required
          disabled={loading}
        />

        <input
          type="password"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
          }
          placeholder="Пароль"
          required
          disabled={loading}
        />

        <button
          type="submit"
          disabled={loading}
        >
          {loading
            ? "Создание..."
            : "Создать аккаунт"}
        </button>
      </form>
    </div>
  );
}