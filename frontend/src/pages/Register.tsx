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
    setMsg("Loading...");
    try {
      await registerUser(name, password);
      setMsg("Registered successfully! Redirecting to login...");
      navigate("/login");
    } catch (err: any) {
      setMsg("Error: " + err.message);
    }
  };

  return (
    <div className="panel default-box">
      <h2>Register</h2>
      <form onSubmit={handleRegister} style={{display: 'contents'}}>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Name"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
        />
        <button type="submit">Create account</button>
      </form>
      <div className="msg">{msg}</div>
    </div>
  );
}