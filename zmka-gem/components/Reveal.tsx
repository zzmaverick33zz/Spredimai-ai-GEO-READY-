"use client";

import { LazyMotion, domAnimation, m } from "framer-motion";
import type { ReactNode } from "react";

/** steps(6): the reveal jumps in six frames instead of easing. */
const steps6 = (t: number) => (t >= 1 ? 1 : Math.floor(t * 6) / 6);

/**
 * Fade + 24px rise, once, when the section enters the viewport.
 * Same markup on server and client; reduced motion is handled in CSS (.reveal).
 */
export function Reveal({ children }: { children: ReactNode }) {
  return (
    <LazyMotion features={domAnimation} strict>
      <m.div
        className="reveal"
        initial={{ opacity: 0, y: 24 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "0px 0px -10% 0px" }}
        transition={{ duration: 0.6, ease: steps6 }}
      >
        {children}
      </m.div>
    </LazyMotion>
  );
}
