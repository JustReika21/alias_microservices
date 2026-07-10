import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useToast } from "../components/ToastProvider";

export default function Login() {
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const { login } = useAuth();
  const { showToast } = useToast();


  const handleLogin = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    if (loading) return;

    setLoading(true);

    try {
      await login(name, password);

      showToast(
        "Вы успешно вошли",
        "success"
      );

      navigate("/");

    } catch (err: any) {

      showToast(
        err.message || "Не удалось войти",
        "error"
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel default-box">
      <h2>Вход</h2>

      <input
        value={name}
        onChange={(e) =>
          setName(e.target.value)
        }
        placeholder="Имя"
        disabled={loading}
      />

      <input
        type="password"
        value={password}
        onChange={(e) =>
          setPassword(e.target.value)
        }
        placeholder="Пароль"
        disabled={loading}
      />

      <button
        onClick={handleLogin}
        disabled={loading}
      >
        {loading ? "Вход..." : "Войти"}
      </button>
    </div>
  );
}