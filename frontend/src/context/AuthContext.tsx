import { createContext, useContext, useState, useEffect } from "react"
import { loginUser, logoutUser } from "../services/authService"
import { getUser, refreshAccessToken } from "../services/api"

type AuthContextType = {
  user: boolean
  loading: boolean
  login: (name: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const init = async () => {
      const token = localStorage.getItem("access_token")

      if (!token) {
        try {
          await refreshAccessToken()
          const u = await getUser()
          setUser(!!u)
        } catch {
          localStorage.removeItem("access_token")
          setUser(false)
        }
        setLoading(false)
        return
      }

      try {
        const u = await getUser()
        if (!u) {
          await refreshAccessToken()
          const u2 = await getUser()
          setUser(!!u2)
        } else {
          setUser(true)
        }
      } catch {
        localStorage.removeItem("access_token")
        setUser(false)
      }

      setLoading(false)
    }

    init()
  }, [])

  const login = async (name: string, password: string) => {
    await loginUser(name, password)
    setUser(true)
  }

  const logout = async () => {
    await logoutUser()
    setUser(false)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("AuthContext missing")
  return ctx
}
