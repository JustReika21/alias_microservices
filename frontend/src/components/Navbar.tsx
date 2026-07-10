import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useToast } from "./ToastProvider.tsx";

export default function Navbar() {
  const { user, logout, loading } = useAuth();
  const { showToast } = useToast();

  if (loading) return null;


  async function handleLogout() {
    try {
      await logout();

      showToast(
        "Вы вышли из аккаунта",
        "success"
      );

    } catch (err: any) {

      showToast(
        err.message || "Не удалось выйти",
        "error"
      );

    }
  }


  return (
    <nav className="navbar">
      <Link
        to="/"
        className="navbar-brand"
      >
        Алиас
      </Link>

      <input
        id="nav-toggle"
        type="checkbox"
      />

      <label
        htmlFor="nav-toggle"
        className="navbar-burger"
      >
        ☰
      </label>


      <div className="navbar-links">

        <Link
          to="/pack/create"
          className="navbar-link"
        >
          Создать пак
        </Link>


        <Link
          to="/game/create"
          className="navbar-link"
        >
          Создать игру
        </Link>


        {user && (
          <Link
            to="/packs/my"
            className="navbar-link"
          >
            Мои паки
          </Link>
        )}

        <Link
          to="/rules"
          className="navbar-link"
        >
          Правила
        </Link>


        {!user ? (
          <>
            <Link
              to="/register"
              className="navbar-link"
            >
              Регистрация
            </Link>

            <Link
              to="/login"
              className="navbar-link"
            >
              Вход
            </Link>
          </>
        ) : (
          <button
            onClick={handleLogout}
            className="navbar-link"
            style={{
              background: "none",
              border: "none",
              padding: 0,
              font: "inherit",
              cursor: "pointer",
            }}
          >
            Выход
          </button>
        )}

      </div>
    </nav>
  );
}