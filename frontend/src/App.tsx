import { Routes, Route } from "react-router-dom"
import PrivateRoute from "./components/PrivateRoute"
import Navbar from "./components/Navbar"

import Register from "./pages/Register"
import Main from "./pages/Main"
import Login from "./pages/Login"
import CreatePack from "./pages/CreatePack"
import EditPack from "./pages/EditPack"
import CreateGame from "./pages/CreateGame"
import GamePage from "./pages/GamePage"
import MyPacks from "./pages/MyPacks.tsx";
import Rules from  "./pages/Rules.tsx"

function App() {
  return (
    <>
      <Navbar />

      <Routes>
        <Route path="/" element={<Main />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/rules" element={<Rules />} />

        <Route
          path="/pack/create"
          element={
            <PrivateRoute>
              <CreatePack />
            </PrivateRoute>
          }
        />
        <Route
          path="/packs/my"
          element={
            <PrivateRoute>
              <MyPacks />
            </PrivateRoute>
          }
        />
        <Route
          path="/pack/edit/:packId"
          element={
            <PrivateRoute>
              <EditPack />
            </PrivateRoute>
          }
        />
        <Route
          path="/game/create"
          element={
            <PrivateRoute>
              <CreateGame />
            </PrivateRoute>
          }
        />
        <Route
          path="/game/:gameId"
          element={
            <PrivateRoute>
              <GamePage />
            </PrivateRoute>
          }
        />
      </Routes>
    </>
  )
}

export default App
