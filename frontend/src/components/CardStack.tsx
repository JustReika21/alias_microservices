import { useCardSlider } from "../hooks/useCardSlider";
import { useEffect, useRef } from "react";

interface CardStackProps {
  cards: any[];
  guessedMap: Record<number, boolean>;
  status: string;
  sendAction: (msg: any) => void;
}

export default function CardStack({
  cards,
  guessedMap,
  status,
  sendAction,
}: CardStackProps) {
  const { index, next, prev, setIndex } =
    useCardSlider(cards.length);

  const prevLengthRef = useRef(cards.length);

  const hasCards = cards.length > 0;

  const safeNext = () => {
    if (!hasCards) return;
    next();
  };

  const safePrev = () => {
    if (!hasCards) return;
    prev();
  };

  useEffect(() => {
    if (cards.length === 0) {
      setIndex(0);
    } else {
      if (index > cards.length - 1) {
        setIndex(cards.length - 1);
      }

      if (
        cards.length >
        prevLengthRef.current
      ) {
        setIndex(cards.length - 1);
      }
    }

    prevLengthRef.current = cards.length;
  }, [cards.length, index, setIndex]);

  const getCardClass = (
    card: any,
    offset: number
  ) => {
    let cls = "card-item";

    if (offset < 0) cls += " left";
    else if (offset > 0) cls += " right";
    else cls += " center";

    if (status === "calculating") {
      if (guessedMap[card.id] === false) {
        cls += " not-guessed";
      } else {
        cls += " guessed";
      }
    }

    return cls;
  };

  return (
    <div
      className="card-stack-wrapper"
    >
      <div className="card-stack">
        {cards.map((card, i) => {
          const offset = i - index;

          if (Math.abs(offset) > 2)
            return null;

          return (
            <div
              key={card.id}
              className={getCardClass(
                card,
                offset
              )}
              style={{
                transform: `translateX(${
                  offset * 120
                }%) scale(${
                  offset === 0 ? 1 : 0.85
                })`,
                zIndex:
                  100 - Math.abs(offset),
                opacity:
                  Math.abs(offset) > 1
                    ? 0
                    : Math.abs(offset) === 1
                    ? 0.6
                    : 1,
                filter:
                  offset !== 0
                    ? "blur(2px)"
                    : "none",
                transition:
                  "all 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
              }}
            >
              <div className="card-word">
                {card.word}
              </div>

              {status ===
                "calculating" &&
                i === index && (
                  <div className="card-actions">
                    <button
                      onClick={() =>
                        sendAction({
                          type: "guessed",
                          card: card.id,
                        })
                      }
                    >
                      GUESSED
                    </button>

                    <button
                      onClick={() =>
                        sendAction({
                          type:
                            "not_guessed",
                          card: card.id,
                        })
                      }
                    >
                      NOT GUESSED
                    </button>
                  </div>
                )}
            </div>
          );
        })}
      </div>

      <div className="card-nav">
        <button
          onClick={safePrev}
          disabled={
            !hasCards || index === 0
          }
        >
          ←
        </button>

        <span>
          {hasCards
            ? `${index + 1} / ${cards.length}`
            : "0 / 0"}
        </span>

        <button
          onClick={safeNext}
          disabled={
            !hasCards ||
            index === cards.length - 1
          }
        >
          →
        </button>
      </div>
    </div>
  );
}