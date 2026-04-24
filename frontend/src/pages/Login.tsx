import { useState } from "react";
import { loginUser } from "../services/authService";

export default function Login() {
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");

  const handleLogin = async () => {
    setMsg("Loading...");
    try {
      await loginUser(name, password);
      setMsg("Login successfully!");
    } catch (err: any) {
      setMsg("Error: " + err.message);
    }
  };

  return (
    <div className="box">
      <h2>Login</h2>
      <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" />
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
      <button onClick={handleLogin}>Login</button>
      <div className="msg">{msg}</div>
    </div>
  );
}