import { createRoot } from "react-dom/client"
import { BrowserRouter } from "react-router-dom"

import "./index.css"
import "./styles/Auth.css"
import "./styles/Navbar.css"
import "./styles/CardStack.css"
import "./styles/TeamGrid.css"
import "./styles/GameButton.css"
import "./styles/EditPack.css"
import "./styles/MyPacks.css"
import "./styles/CreateGame.css"
import "./styles/Main.css";
import "./styles/Rules.css"

import App from "./App"
import { AuthProvider } from "./context/AuthContext"
import { ToastProvider } from "./components/ToastProvider";

createRoot(document.getElementById("root")!).render(
  <ToastProvider>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </ToastProvider>
)
