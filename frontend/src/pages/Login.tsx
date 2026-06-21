import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

export default function Login() {
  const [name, setName] = useState("")
  const [password, setPassword] = useState("")
  const [msg, setMsg] = useState("")
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setMsg("Загрузка...")

    try {
      await login(name, password)
      navigate("/")
    } catch (err: any) {
      setMsg("Ошибка: " + (err.message || "Не удалось войти"))
    }
  }

  return (
    <div className="panel default-box">
      <h2>Вход</h2>

      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Имя"
      />

      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Пароль"
      />

      <button onClick={handleLogin}>Войти</button>

      <div className="msg">{msg}</div>
    </div>
  )
}