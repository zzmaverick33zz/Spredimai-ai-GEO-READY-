"use client";

import Image from "next/image";
import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { format, type Locale, type Messages } from "@/lib/i18n";
import { work, type WorkItem } from "@/content/work";
import { ExternalLink, container, h2Class } from "@/components/ui";
import { site } from "@/content/site";

function Placeholder({ label, word }: { label: string; word: string }) {
  return (
    <span className="absolute inset-0 flex items-end bg-blush p-5">
      <span className="dither-dense opacity-50" />
      <span className="relative rounded-full bg-white px-3.5 py-1.5 text-xs font-semibold">
        [ {word} · {label} ]
      </span>
    </span>
  );
}

function Lightbox({
  items,
  index,
  locale,
  t,
  onClose,
  onIndex,
}: {
  items: WorkItem[];
  index: number;
  locale: Locale;
  t: Messages["work"];
  onClose: () => void;
  onIndex: (i: number) => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const item = items[index];
  const go = useCallback((d: number) => onIndex((index + d + items.length) % items.length), [index, items.length, onIndex]);

  useEffect(() => {
    closeRef.current?.focus();
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      else if (e.key === "ArrowRight") go(1);
      else if (e.key === "ArrowLeft") go(-1);
      else if (e.key === "Tab" && ref.current) {
        const f = ref.current.querySelectorAll<HTMLElement>("button");
        const first = f[0];
        const last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [go, onClose]);

  const navBtn =
    "inline-flex size-12 items-center justify-center rounded-full border-[1.5px] border-ink bg-white text-ink hover:bg-blush active:bg-blush";

  // Portal: section wrappers use transform (reveal), which would trap position: fixed.
  return createPortal(
    <div
      ref={ref}
      role="dialog"
      aria-modal="true"
      aria-label={t.dialog}
      className="fixed inset-0 z-[70] flex flex-col bg-white/97 p-4 sm:p-8"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="dither-dense opacity-20" />
      <div className="relative flex items-center justify-between gap-4">
        <p className="m-0 font-display text-sm font-semibold" aria-live="polite">
          {item.label} <span className="text-gray-soft">· {format(t.counter, { n: index + 1, total: items.length })}</span>
        </p>
        <button ref={closeRef} type="button" onClick={onClose} className={navBtn} aria-label={t.close}>
          <svg aria-hidden="true" width="16" height="16" viewBox="0 0 16 16" shapeRendering="crispEdges">
            <path d="M0 0h2v2H0zM2 2h2v2H2zM4 4h2v2H4zM6 6h4v4H6zM10 4h2v2h-2zM12 2h2v2h-2zM14 0h2v2h-2zM4 10h2v2H4zM2 12h2v2H2zM0 14h2v2H0zM10 10h2v2h-2zM12 12h2v2h-2zM14 14h2v2h-2z" fill="currentColor" />
          </svg>
        </button>
      </div>
      <div className="relative flex min-h-0 flex-1 items-center justify-center py-4" onClick={(e) => e.target === e.currentTarget && onClose()}>
        {item.src ? (
          <Image
            key={item.src}
            src={item.src}
            alt={item.alt[locale]}
            width={item.width}
            height={item.height}
            sizes="(min-width: 1024px) 60vw, 92vw"
            className="max-h-full w-auto max-w-full rounded-[24px] object-contain"
            style={{ height: "100%", width: "auto" }}
          />
        ) : (
          <div className="relative aspect-[4/5] h-full max-w-full overflow-hidden rounded-[24px]">
            <Placeholder label={item.label} word={t.placeholder} />
          </div>
        )}
      </div>
      <div className="relative flex justify-center gap-4">
        <button type="button" onClick={() => go(-1)} className={navBtn} aria-label={t.prev}>
          <svg aria-hidden="true" width="14" height="14" viewBox="0 0 14 14" shapeRendering="crispEdges">
            <path d="M8 0h2v2H8zM6 2h2v2H6zM4 4h2v2H4zM2 6h12v2H2zM4 8h2v2H4zM6 10h2v2H6zM8 12h2v2H8z" fill="currentColor" />
          </svg>
        </button>
        <button type="button" onClick={() => go(1)} className={navBtn} aria-label={t.next}>
          <svg aria-hidden="true" width="14" height="14" viewBox="0 0 14 14" shapeRendering="crispEdges">
            <path d="M4 0h2v2H4zM6 2h2v2H6zM8 4h2v2H8zM0 6h12v2H0zM8 8h2v2H8zM6 10h2v2H6zM4 12h2v2H4z" fill="currentColor" />
          </svg>
        </button>
      </div>
    </div>,
    document.body,
  );
}

export function Work({ locale, t, newTab }: { locale: Locale; t: Messages["work"]; newTab: string }) {
  const [open, setOpen] = useState<number | null>(null);
  const triggers = useRef<(HTMLButtonElement | null)[]>([]);

  const opener = useRef<number | null>(null);

  const show = (i: number) => {
    opener.current = i;
    setOpen(i);
  };
  const close = useCallback(() => {
    setOpen(null);
    // Return focus to the tile that opened the viewer.
    const i = opener.current;
    if (i !== null) setTimeout(() => triggers.current[i]?.focus(), 0);
  }, []);

  return (
    <section id="work" aria-labelledby="work-title" className={`${container} pb-10 pt-12 sm:pt-16`}>
      <div className="mb-12 flex flex-wrap items-end justify-between gap-6">
        <h2 id="work-title" className={h2Class}>
          {t.title}
        </h2>
        <ExternalLink
          href={site.instagram}
          newTabLabel={newTab}
          className="inline-flex min-h-11 items-center border-b-2 border-magenta font-semibold hover:text-pink-deep"
        >
          <span translate="no">{t.instagram}</span>
        </ExternalLink>
      </div>

      <ul className="m-0 grid list-none grid-cols-1 items-start gap-6 p-0 sm:grid-cols-2 lg:grid-cols-3">
        {work.map((w, i) => (
          <li
            key={w.label}
            className="sm:[&:nth-child(even)]:mt-12 lg:[&:nth-child(even)]:mt-0 lg:[&:nth-child(3n+2)]:mt-12"
          >
            <button
              ref={(el) => {
                triggers.current[i] = el;
              }}
              type="button"
              onClick={() => show(i)}
              aria-haspopup="dialog"
              className="tile group block w-full cursor-zoom-in rounded-[24px] text-left"
            >
              <span
                className="relative block overflow-hidden rounded-[24px] bg-blush"
                style={{ aspectRatio: w.ratio }}
              >
                {w.src ? (
                  <Image
                    src={w.src}
                    alt={w.alt[locale]}
                    fill
                    sizes="(min-width: 1024px) 400px, (min-width: 640px) 50vw, 100vw"
                    className="object-cover"
                  />
                ) : (
                  <Placeholder label={w.label} word={t.placeholder} />
                )}
              </span>
              <span className="mt-3 flex items-center gap-2 font-display text-[13px] font-semibold">
                <span aria-hidden="true" className="diamond block size-2 bg-magenta" />
                <span className="sr-only">{t.open}:</span> {w.label}
              </span>
            </button>
          </li>
        ))}
      </ul>

      {open !== null && (
        <Lightbox items={work} index={open} locale={locale} t={t} onClose={close} onIndex={setOpen} />
      )}
    </section>
  );
}
