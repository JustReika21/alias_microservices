import { Link } from "react-router-dom";

export default function Main() {
  return (
    <div>
      <h1>Main page</h1>
      <Link to="/login">Go to Login</Link>
    </div>
  );
}