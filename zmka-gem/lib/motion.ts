"use client";

import { useEffect, useState } from "react";

const KEY = "zmka-motion";
const EVENT = "zmka:motion";

export function isPaused(): boolean {
  return document.documentElement.dataset.motion === "paused";
}

export function setPaused(paused: boolean): void {
  document.documentElement.dataset.motion = paused ? "paused" : "running";
  try {
    localStorage.setItem(KEY, paused ? "paused" : "running");
  } catch {
    /* storage unavailable: the toggle still works for this page view */
  }
  window.dispatchEvent(new Event(EVENT));
}

export function restorePaused(): void {
  try {
    if (localStorage.getItem(KEY) === "paused") setPaused(true);
  } catch {
    /* ignore */
  }
}

/** True when decorative motion should run: no reduced-motion, not paused. */
export function useMotionAllowed(): boolean {
  const [allowed, setAllowed] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setAllowed(!mq.matches && !isPaused());
    update();
    mq.addEventListener("change", update);
    window.addEventListener(EVENT, update);
    return () => {
      mq.removeEventListener("change", update);
      window.removeEventListener(EVENT, update);
    };
  }, []);
  return allowed;
}

export function usePausedState(): boolean {
  const [paused, set] = useState(false);
  useEffect(() => {
    const update = () => set(isPaused());
    update();
    window.addEventListener(EVENT, update);
    return () => window.removeEventListener(EVENT, update);
  }, []);
  return paused;
}
