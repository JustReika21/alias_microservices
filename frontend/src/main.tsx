import { StrictMode } from "react"
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

import App from "./App"
import { AuthProvider } from "./context/AuthContext"

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
)
