"use client";

import { useEffect, useRef, useState } from "react";
import { useMotionAllowed } from "@/lib/motion";

const COUNT = 8;
const GRID = 4; // snap to a 4px grid so the trail reads as pixels

/** Magenta pixel trail behind the cursor. Desktop (fine pointer) only. */
export function CursorTrail() {
  const allowed = useMotionAllowed();
  const [finePointer, setFinePointer] = useState(false);
  const dots = useRef<(HTMLSpanElement | null)[]>([]);

  useEffect(() => {
    const mq = window.matchMedia("(hover: hover) and (pointer: fine)");
    const update = () => setFinePointer(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, []);

  const active = allowed && finePointer;

  useEffect(() => {
    if (!active) return;
    const pts = Array.from({ length: COUNT }, () => ({ x: -100, y: -100 }));
    const target = { x: -100, y: -100 };
    let raf = 0;
    let idle = 0;
    let frame = 0;

    const tick = () => {
      frame++;
      // Update every other frame: a stepped, low-fps feel.
      if (frame % 2 === 0) {
        pts[0].x = target.x;
        pts[0].y = target.y;
        for (let i = COUNT - 1; i > 0; i--) {
          pts[i].x += (pts[i - 1].x - pts[i].x) * 0.6;
          pts[i].y += (pts[i - 1].y - pts[i].y) * 0.6;
        }
        let moving = false;
        pts.forEach((p, i) => {
          const el = dots.current[i];
          if (!el) return;
          const x = Math.round(p.x / GRID) * GRID;
          const y = Math.round(p.y / GRID) * GRID;
          el.style.transform = `translate3d(${x}px, ${y}px, 0)`;
          if (Math.abs(p.x - target.x) > 1 || Math.abs(p.y - target.y) > 1) moving = true;
        });
        idle = moving ? 0 : idle + 1;
      }
      if (idle < 6) raf = requestAnimationFrame(tick);
      else {
        raf = 0;
        dots.current.forEach((el) => el && (el.style.opacity = "0"));
      }
    };

    const onMove = (e: PointerEvent) => {
      if (e.pointerType !== "mouse") return;
      target.x = e.clientX;
      target.y = e.clientY;
      idle = 0;
      dots.current.forEach((el, i) => el && (el.style.opacity = String(1 - Math.floor((i * 4) / COUNT) * 0.22)));
      if (!raf) raf = requestAnimationFrame(tick);
    };

    window.addEventListener("pointermove", onMove, { passive: true });
    return () => {
      window.removeEventListener("pointermove", onMove);
      if (raf) cancelAnimationFrame(raf);
    };
  }, [active]);

  if (!active) return null;

  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 z-[60]">
      {Array.from({ length: COUNT }, (_, i) => {
        const size = i < 3 ? 6 : i < 6 ? 5 : 4;
        return (
          <span
            key={i}
            ref={(el) => {
              dots.current[i] = el;
            }}
            className="absolute left-0 top-0 block bg-magenta"
            style={{
              width: size,
              height: size,
              marginLeft: 8,
              marginTop: 10,
              opacity: 0,
              transform: "translate3d(-100px,-100px,0)",
            }}
          />
        );
      })}
    </div>
  );
}
