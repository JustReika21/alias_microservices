import { Link } from "react-router-dom";
import {useEffect} from "react";

export default function Main() {
  useEffect(() => {
    document.title = "Алиас";
  }, []);
  return (
    <main className="main-page">
      <div className="hero">

        <div className="hero-content">
          <div className="logo">
            Алиас<span>.</span>
          </div>

          <h1>
            Объясняй слова.
            <br />
            <span>Соревнуйся с друзьями.</span>
          </h1>

          <p>
            Онлайн игра Alias, где один объясняет слово,
            а команда пытается угадать как можно больше.
          </p>

          <div className="hero-buttons">
            <Link to="/game/create" className="main-button">
              Начать игру
            </Link>

            <Link to="/register" className="secondary-button">
              Зарегестрироваться
            </Link>
          </div>
        </div>

        <div className="game-preview">

          <div className="word-card card-one">
            <span>Игра</span>
            <strong>Алиас</strong>
          </div>

          <div className="word-card card-two">
            <span>Объясни</span>
            <strong>Своей команде</strong>
          </div>

          <div className="word-card card-three">
            <span>Время</span>
            <strong>03:55</strong>
          </div>

        </div>

      </div>

      <section className="features">

        <div>
          <h3>Создатель</h3>
          <p>
            Максим JustReika21 Мисюрин. <br/> <a href={"https://github.com/JustReika21/alias_microservices"}>Проект</a> на GitHub
          </p>
        </div>

        <div>
          <h3>Настольная игра</h3>
          <p>
            Для проведения приятных вечеров в хорошей компании.
          </p>
        </div>

        <div>
          <h3>Beta v1.0</h3>
          <p>
            Не ругайтесь на баги, все починю. Приятной вам игры
          </p>
        </div>
      </section>
    </main>
  );
}