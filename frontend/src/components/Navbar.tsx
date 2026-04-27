import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const location = useLocation();

  const isActive = (path: string): boolean => location.pathname === path;

  return (
    <nav className="navbar">
      <Link to="/" className={`navbar-brand ${isActive("/") ? "active" : ""}`}>
        Alias
      </Link>
      <div className="navbar-links">
        <Link to="/pack/create" className={isActive("/pack/create") ? "active" : ""}>
          Create pack
        </Link>
        <Link to="/game/create" className={isActive("/game/create") ? "active" : ""}>
          Create game
        </Link>
        <Link to="/register" className={isActive("/register") ? "active" : ""}>
          Register
        </Link>
        <Link to="/login" className={isActive("/login") ? "active" : ""}>
          Login
        </Link>
      </div>
    </nav>
  );
}