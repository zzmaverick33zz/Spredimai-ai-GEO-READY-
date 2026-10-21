"use client";

import { useEffect } from "react";
import { restorePaused, setPaused, usePausedState } from "@/lib/motion";

export function MotionToggle({ pauseLabel, playLabel }: { pauseLabel: string; playLabel: string }) {
  const paused = usePausedState();
  useEffect(() => restorePaused(), []);
  return (
    <button
      type="button"
      aria-pressed={paused}
      onClick={() => setPaused(!paused)}
      className="inline-flex min-h-11 cursor-pointer items-center gap-2 rounded-full border-[1.5px] border-ink bg-white px-[18px] text-sm font-semibold text-ink hover:bg-blush active:bg-blush"
    >
      <svg aria-hidden="true" width="10" height="10" viewBox="0 0 10 10" shapeRendering="crispEdges">
        {paused ? (
          <path d="M0 0h2v10H0zM2 2h2v6H2zM4 3h2v4H4zM6 4h2v2H6z" fill="currentColor" />
        ) : (
          <path d="M1 0h3v10H1zM6 0h3v10H6z" fill="currentColor" />
        )}
      </svg>
      {paused ? playLabel : pauseLabel}
    </button>
  );
}
