import { useState } from "react";
import { registerUser } from "../services/authService";
import { useNavigate } from "react-router-dom";

export default function Register() {
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg("Загрузка...");

    try {
      await registerUser(name, password);
      setMsg("Регистрация успешна! Переход к входу...");
      navigate("/login");
    } catch (err: any) {
      setMsg("Ошибка: " + (err.message || "Не удалось зарегистрироваться"));
    }
  };

  return (
    <div className="panel default-box">
      <h2>Регистрация</h2>

      <form onSubmit={handleRegister} style={{ display: "contents" }}>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Имя"
          required
        />

        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Пароль"
          required
        />

        <button type="submit">Создать аккаунт</button>
      </form>

      <div className="msg">{msg}</div>
    </div>
  );
}