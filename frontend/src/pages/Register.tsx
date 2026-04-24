import { useState } from "react";
import { registerUser } from "../services/authService";

export default function Register() {
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");

  const handleRegister = async () => {
    setMsg("Loading...");
    try {
      await registerUser(name, password);
      setMsg("Registered successfully!");
    } catch (err: any) {
      setMsg("Error: " + err.message);
    }
  };

  return (
    <div className="box">
      <h2>Register</h2>
      <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" />
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
      <button onClick={handleRegister}>Create account</button>
      <div className="msg">{msg}</div>
    </div>
  );
}