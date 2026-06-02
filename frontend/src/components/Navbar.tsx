import { Link, useLocation } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

export default function Navbar() {
  const location = useLocation()
  const { user, logout, loading } = useAuth()

  const isActive = (path: string) =>
    location.pathname.startsWith(path)

  const linkClass = (path?: string) =>
    `navbar-link${path && isActive(path) ? " active" : ""}`

  if (loading) return null

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">Alias</Link>

      <div className="navbar-links">

        <Link to="/pack/create" className={linkClass("/pack/create")}>
          Create pack
        </Link>

        <Link to="/game/create" className={linkClass("/game/create")}>
          Create game
        </Link>

        {user && (
          <Link to="/packs/my" className={linkClass("/packs/my")}>
            My packs
          </Link>
        )}

        {!user ? (
          <>
            <Link to="/register" className={linkClass("/register")}>
              Register
            </Link>
            <Link to="/login" className={linkClass("/login")}>
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