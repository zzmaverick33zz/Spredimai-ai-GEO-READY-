import type { ComponentProps, ReactNode } from "react";

/** Shared class strings so sections stay on one rhythm. */
export const container = "mx-auto w-full max-w-[1240px] px-4 sm:px-8";
export const h2Class =
  "m-0 font-display font-extrabold text-[clamp(32px,4vw,56px)] leading-[1.05] tracking-[-0.02em]";
export const btnPrimary =
  "btn-pixel inline-flex min-h-11 items-center justify-center rounded-full bg-ink px-8 py-4 text-base font-semibold text-white hover:text-white focus-visible:text-white";
export const btnOutline =
  "inline-flex min-h-11 items-center justify-center rounded-full border-[1.5px] border-ink bg-white px-7 py-[14px] text-base font-semibold text-ink transition-colors duration-150 [transition-timing-function:steps(3)] hover:bg-blush active:bg-blush";

export function Diamond({ className = "", size = 10 }: { className?: string; size?: number }) {
  return (
    <span
      aria-hidden="true"
      className={`diamond block shrink-0 ${className}`}
      style={{ width: size, height: size }}
    />
  );
}

/** External link that announces it opens in a new tab. */
export function ExternalLink({
  children,
  newTabLabel,
  ...props
}: ComponentProps<"a"> & { newTabLabel: string; children: ReactNode }) {
  return (
    <a target="_blank" rel="noopener" {...props}>
      {children}
      <span className="sr-only"> ({newTabLabel})</span>
    </a>
  );
}
