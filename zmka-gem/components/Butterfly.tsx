import Image from "next/image";

type Drift = "drift-1" | "drift-2" | "drift-3";

/**
 * Two layers: outer `drift` moves along the path, inner `flap` squashes
 * scaleX for the wing beat. Both run on steps() for the 8-bit feel.
 */
export function Butterfly({
  drift,
  flap = "flap",
  className = "",
  children,
}: {
  drift: Drift;
  flap?: "flap" | "flap-slow";
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div aria-hidden="true" className={`pointer-events-none absolute ${drift} ${className}`}>
      <div className={flap}>{children}</div>
    </div>
  );
}

/**
 * Pixel sprite shown at an integer scale only (image-rendering: pixelated).
 * `scale` is applied to the native sprite size, so 48 × 2 = 96px.
 */
export function Sprite({
  size,
  scale,
  light = false,
  className = "",
}: {
  size: 16 | 32 | 48;
  scale: number;
  light?: boolean;
  className?: string;
}) {
  const px = size * scale;
  return (
    <Image
      src={`/brand/butterfly-sprite-${light ? "light-" : ""}${size}.png`}
      alt=""
      width={px}
      height={px}
      unoptimized
      loading="lazy"
      className={`pixelated block ${className}`}
    />
  );
}

/**
 * Dithered butterfly (not pixelated: it is a downscale of a large image).
 * The WebP files are already optimised by scripts/prepare_assets.py, so they are
 * served as is with a srcset; routing them through the image optimiser only
 * delays the hero LCP.
 */
export function DitherButterfly({
  size,
  light = false,
  priority = false,
  alt = "",
  sizes,
  className = "",
}: {
  size: number;
  light?: boolean;
  priority?: boolean;
  alt?: string;
  sizes?: string;
  className?: string;
}) {
  const base = `/brand/butterfly${light ? "-light" : ""}`;
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={`${base}-440.webp`}
      srcSet={`${base}-440.webp 440w, ${base}-600.webp 600w, ${base}-880.webp 880w`}
      sizes={sizes ?? `${size}px`}
      alt={alt}
      width={size}
      height={size}
      decoding={priority ? "sync" : "async"}
      fetchPriority={priority ? "high" : undefined}
      loading={priority ? "eager" : "lazy"}
      className={`block h-auto w-full ${className}`}
    />
  );
}
