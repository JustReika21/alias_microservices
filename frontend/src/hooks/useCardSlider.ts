import { useState } from "react";

export function useCardSlider(length: number) {
  const [index, setIndex] = useState(0);

  function next() {
    setIndex((i) => Math.min(i + 1, length - 1));
  }

  function prev() {
    setIndex((i) => Math.max(i - 1, 0));
  }


  return { index, next, prev, setIndex };
}