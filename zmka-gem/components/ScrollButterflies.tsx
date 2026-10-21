"use client";

import { useEffect, useRef } from "react";
import { Sprite } from "@/components/Butterfly";
import { useMotionAllowed } from "@/lib/motion";

/** Up to four small butterflies drifting through the viewport with parallax. */
const flyers = [
  { x: 6, speed: 0.35, offset: 0.15, size: 32 as const, scale: 2, sway: 40 },
  { x: 84, speed: 0.55, offset: 0.55, size: 48 as const, scale: 1, sway: 28 },
  { x: 62, speed: 0.25, offset: 0.85, size: 32 as const, scale: 1, sway: 22 },
  { x: 24, speed: 0.45, offset: 0.4, size: 32 as const, scale: 1, sway: 34 },
];
const STEP = 4; // snap translate to a pixel grid

export function ScrollButterflies() {
  const allowed = useMotionAllowed();
  const refs = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    if (!allowed) return;
    let raf = 0;
    const render = () => {
      raf = 0;
      const vh = window.innerHeight;
      const span = vh + 200;
      const y = window.scrollY;
      flyers.forEach((f, i) => {
        const el = refs.current[i];
        if (!el) return;
        // Travel bottom → top as the page scrolls, wrapping around.
        let pos = (f.offset * span - y * f.speed) % span;
        if (pos < 0) pos += span;
        const ty = Math.round((pos - 100) / STEP) * STEP;
        const tx = Math.round((Math.sin((y * f.speed) / 180 + i) * f.sway) / STEP) * STEP;
        el.style.transform = `translate3d(${tx}px, ${ty}px, 0)`;
      });
    };
    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(render);
    };
    render();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      if (raf) cancelAnimationFrame(raf);
    };
  }, [allowed]);

  if (!allowed) return null;

  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 z-30 overflow-hidden">
      {flyers.map((f, i) => (
        <div
          key={i}
          ref={(el) => {
            refs.current[i] = el;
          }}
          className="absolute top-0 opacity-80"
          style={{ left: `${f.x}%` }}
        >
          <div className={i % 2 ? "flap-slow" : "flap"}>
            <Sprite size={f.size} scale={f.scale} />
          </div>
        </div>
      ))}
    </div>
  );
}
