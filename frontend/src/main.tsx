import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import './index.css'
import './styles/Auth.css';
import './styles/Navbar.css'
import './styles/CardStack.css'
import './styles/TeamGrid.css'
import './styles/GameButton.css'


import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
