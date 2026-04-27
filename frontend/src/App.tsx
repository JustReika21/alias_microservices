import { BrowserRouter, Routes, Route } from "react-router-dom";
import PrivateRoute from "./components/PrivateRoute";

import Navbar from "./components/Navbar.tsx";

import Register from "./pages/Register";
import Main from "./pages/Main";
import Login from "./pages/Login";
import CreatePack from "./pages/CreatePack.tsx";
import EditPack from "./pages/EditPack.tsx";
import CreateGame from "./pages/CreateGame.tsx";
import GamePage from "./pages/GamePage.tsx";


function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <Routes>
        <Route path="/" element={<Main />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/pack/create"
          element={
            <PrivateRoute>
              <CreatePack />
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
    </BrowserRouter>
  );
}

export default App;