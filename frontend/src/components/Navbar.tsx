import { Link } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

export default function Navbar() {
  const { user, logout, loading } = useAuth()

  if (loading) return null

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">Alias</Link>

      <div className="navbar-links">
        <Link to="/pack/create" className="navbar-link">
          Create pack
        </Link>

        <Link to="/game/create" className="navbar-link">
          Create game
        </Link>

        {user && (
          <Link to="/packs/my" className="navbar-link">
            My packs
          </Link>
        )}

        {!user ? (
          <>
            <Link to="/register" className="navbar-link">
              Register
            </Link>
            <Link to="/login" className="navbar-link">
              Login
            </Link>
          </>
        ) : (
          <button
            onClick={logout}
            className="navbar-link"
            style={{
              background: "none",
              border: "none",
              padding: 0,
              font: "inherit",
              cursor: "pointer",
            }}
          >
            Logout
          </button>
        )}
      </div>
    </nav>
  )
}