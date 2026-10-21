import { preload } from "react-dom";
import type { Messages } from "@/lib/i18n";
import { Butterfly, DitherButterfly, Sprite } from "@/components/Butterfly";
import { btnOutline, btnPrimary, container } from "@/components/ui";

const crystals = [
  { className: "left-[12%] bottom-[22%] bg-ink", size: 18, delay: "0s" },
  { className: "right-[10%] top-[12%] bg-magenta", size: 26, delay: ".8s" },
  { className: "right-[30%] bottom-[4%] bg-ink", size: 12, delay: "1.4s" },
  { className: "left-[30%] top-[4%] bg-magenta", size: 10, delay: "2s" },
  { className: "right-[2%] top-[52%] bg-pink-deep", size: 14, delay: "1.1s" },
];

export function Hero({ t }: { t: Messages["hero"] }) {
  // The hero butterfly is the LCP element: start loading it with the HTML.
  preload("/brand/butterfly-440.webp", {
    as: "image",
    imageSrcSet: "/brand/butterfly-440.webp 440w, /brand/butterfly-600.webp 600w, /brand/butterfly-880.webp 880w",
    imageSizes: "(min-width: 1024px) 440px, 280px",
    fetchPriority: "high",
  });
  return (
    <section id="top" aria-labelledby="hero-title" className="relative">
      <div className="dither" />
      <div
        className={`${container} relative grid grid-cols-1 gap-x-8 gap-y-6 pb-20 pt-6 sm:pt-10 lg:grid-cols-[1.25fr_1fr] lg:grid-rows-[auto_auto] lg:pb-24`}
      >
        {/* Text */}
        <div className="flex min-w-0 flex-col gap-6 lg:col-start-1 lg:row-start-1 lg:self-end lg:gap-7">
          <p className="m-0 inline-flex items-center gap-2.5 self-start rounded-full border-[1.5px] border-ink bg-white px-4 py-2 text-[13px] font-medium">
            <span aria-hidden="true" className="block size-2 bg-magenta" />
            {t.badge}
          </p>
          <h1
            id="hero-title"
            className="m-0 font-display text-[clamp(44px,5.8vw,88px)] font-extrabold leading-[0.98] tracking-[-0.02em]"
          >
            {t.titleA}
            <br />
            {t.titleB} <span className="text-pink-deep">{t.titleAccent}</span>
          </h1>
          <p className="m-0 max-w-[480px] text-[17px] leading-relaxed text-gray-text sm:text-[19px]">{t.lead}</p>
        </div>

        {/* Butterflies */}
        <div className="relative mx-auto h-[340px] w-full max-w-[520px] lg:col-start-2 lg:row-span-2 lg:row-start-1 lg:h-[560px] lg:max-w-none">
          <Butterfly
            drift="drift-1"
            className="left-1/2 top-1/2 -ml-[140px] -mt-[150px] w-[280px] lg:-ml-[220px] lg:-mt-[240px] lg:w-[440px]"
          >
            <DitherButterfly size={440} priority sizes="(min-width: 1024px) 440px, 280px" />
          </Butterfly>
          <Butterfly drift="drift-2" flap="flap-slow" className="left-[2%] top-[4%]">
            <Sprite size={48} scale={1} className="lg:hidden" />
            <Sprite size={48} scale={2} className="hidden lg:block" />
          </Butterfly>
          <Butterfly drift="drift-3" className="bottom-[4%] right-[4%]">
            <Sprite size={32} scale={2} className="lg:hidden" />
            <Sprite size={32} scale={4} className="hidden lg:block" />
          </Butterfly>
          {crystals.map((c) => (
            <span
              key={c.className}
              aria-hidden="true"
              className={`diamond twinkle absolute block ${c.className}`}
              style={{ width: c.size, height: c.size, animationDelay: c.delay }}
            />
          ))}
        </div>

        {/* Actions */}
        <div className="flex min-w-0 flex-col gap-5 lg:col-start-1 lg:row-start-2 lg:self-start">
          <div className="flex flex-col gap-4 sm:flex-row sm:flex-wrap sm:items-center">
            <a href="#booking" className={`${btnPrimary} !py-[18px] sm:!px-8`}>
              {t.ctaPrimary}
            </a>
            <a href="#work" className={btnOutline}>
              {t.ctaSecondary}
            </a>
          </div>
          <p className="m-0 flex items-center gap-2 text-sm text-gray-soft">
            <span aria-hidden="true" className="diamond block size-2.5 bg-pink-deep" />
            {t.proof}
          </p>
        </div>
      </div>
    </section>
  );
}
