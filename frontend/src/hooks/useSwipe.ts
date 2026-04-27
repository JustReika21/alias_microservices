import { useRef } from "react";

export function useSwipe(onSwipeLeft: () => void, onSwipeRight: () => void) {
  const startX = useRef(0);
  const endX = useRef(0);

  function onTouchStart(e: React.TouchEvent) {
    startX.current = e.touches[0].clientX;
  }

  function onTouchMove(e: React.TouchEvent) {
    endX.current = e.touches[0].clientX;
  }

  function onTouchEnd() {
    const diff = startX.current - endX.current;

    if (diff > 50) onSwipeLeft();
    if (diff < -50) onSwipeRight();
  }

  return {
    onTouchStart,
    onTouchMove,
    onTouchEnd
  };
}