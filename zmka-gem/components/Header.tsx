"use client";

import Image from "next/image";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { localePath, type Locale, type Messages } from "@/lib/i18n";
import { btnPrimary, container } from "@/components/ui";
import { site } from "@/content/site";

type NavMessages = Messages["nav"];

function useLinks(t: NavMessages) {
  return [
    { href: "#work", label: t.work },
    { href: "#services", label: t.services },
    ...(site.sections.training ? [{ href: "#training", label: t.training }] : []),
    { href: "#booking", label: t.booking },
    { href: "#events", label: t.events },
  ];
}

function LangSwitch({ locale, t, large = false }: { locale: Locale; t: NavMessages; large?: boolean }) {
  const items: { code: Locale; label: string }[] = [
    { code: "en", label: "EN" },
    { code: "lt", label: "LT" },
  ];
  return (
    <ul aria-label={t.language} className={`m-0 flex list-none items-center p-0 ${large ? "gap-2" : ""}`}>
      {items.map((it) => {
        const current = it.code === locale;
        return (
          <li key={it.code}>
            <Link
              href={localePath(it.code)}
              hrefLang={it.code}
              lang={it.code}
              aria-current={current ? "page" : undefined}
              className={`inline-flex min-h-11 min-w-11 items-center justify-center rounded-full ${
                large ? "font-display text-xl" : "text-[13px]"
              } ${current ? "font-semibold text-ink underline decoration-magenta decoration-2 underline-offset-4" : "text-gray-soft hover:text-pink-deep"}`}
            >
              {it.label}
            </Link>
          </li>
        );
      })}
    </ul>
  );
}

function Wordmark({ priority = false }: { priority?: boolean }) {
  return (
    <Image
      src="/brand/wordmark-black.png"
      alt="ZM_KA GEM"
      width={194}
      height={22}
      priority={priority}
      className="block h-[18px] w-auto sm:h-[22px]"
      style={{ width: "auto" }}
    />
  );
}

export function Header({ locale, t }: { locale: Locale; t: NavMessages }) {
  const links = useLinks(t);
  const [open, setOpen] = useState(false);
  const burgerRef = useRef<HTMLButtonElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);

  const close = useCallback((restoreFocus = true) => {
    setOpen(false);
    if (restoreFocus) requestAnimationFrame(() => burgerRef.current?.focus());
  }, []);

  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    closeRef.current?.focus();

    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") close();
      if (e.key !== "Tab" || !menuRef.current) return;
      const focusable = menuRef.current.querySelectorAll<HTMLElement>("a[href], button:not([disabled])");
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };
    document.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = prev;
      document.removeEventListener("keydown", onKey);
    };
  }, [open, close]);

  return (
    <header className="sticky top-0 z-40 bg-white/95">
      <div className={`${container} flex items-center justify-between gap-4 py-3 sm:py-4`}>
        <Link href={localePath(locale)} translate="no" aria-label={t.home} className="flex min-h-11 items-center">
          <Wordmark priority />
        </Link>

        <nav aria-label={t.label} className="hidden items-center gap-x-5 text-sm font-medium lg:flex">
          <ul className="m-0 flex list-none items-center gap-x-5 p-0">
            {links.map((l) => (
              <li key={l.href}>
                <a href={l.href} className="inline-flex min-h-11 items-center hover:text-pink-deep">
                  {l.label}
                </a>
              </li>
            ))}
          </ul>
          <LangSwitch locale={locale} t={t} />
          <a href="#booking" className={`${btnPrimary} !px-[22px] !py-0 !text-sm`}>
            {t.book}
          </a>
        </nav>

        <button
          ref={burgerRef}
          type="button"
          className="inline-flex min-h-11 min-w-11 items-center justify-center gap-2 rounded-full border-[1.5px] border-ink px-4 text-sm font-semibold hover:bg-blush active:bg-blush lg:hidden"
          aria-expanded={open}
          aria-controls="mobile-menu"
          onClick={() => setOpen(true)}
        >
          <svg aria-hidden="true" width="18" height="14" viewBox="0 0 18 14" shapeRendering="crispEdges">
            <rect y="0" width="18" height="2" fill="currentColor" />
            <rect y="6" width="18" height="2" fill="currentColor" />
            <rect y="12" width="18" height="2" fill="currentColor" />
          </svg>
          <span>{t.menu}</span>
        </button>
      </div>

      <div
        id="mobile-menu"
        ref={menuRef}
        hidden={!open}
        className="fixed inset-0 z-50 overflow-y-auto bg-white lg:hidden"
      >
        <div className="dither-dense opacity-25" />
        <div className={`${container} relative flex items-center justify-between py-3`}>
          <span translate="no" className="flex min-h-11 items-center">
            <Wordmark />
          </span>
          <button
            ref={closeRef}
            type="button"
            aria-label={t.closeMenu}
            aria-expanded={open}
            aria-controls="mobile-menu"
            onClick={() => close()}
            className="inline-flex min-h-11 min-w-11 items-center justify-center rounded-full border-[1.5px] border-ink hover:bg-blush"
          >
            <svg aria-hidden="true" width="16" height="16" viewBox="0 0 16 16" shapeRendering="crispEdges">
              <path d="M0 0h2v2H0zM2 2h2v2H2zM4 4h2v2H4zM6 6h4v4H6zM10 4h2v2h-2zM12 2h2v2h-2zM14 0h2v2h-2zM4 10h2v2H4zM2 12h2v2H2zM0 14h2v2H0zM10 10h2v2h-2zM12 12h2v2h-2zM14 14h2v2h-2z" fill="currentColor" />
            </svg>
          </button>
        </div>
        <nav aria-label={t.mobileLabel} className={`${container} relative flex flex-col gap-8 pb-10 pt-6`}>
          <ul className="m-0 flex list-none flex-col gap-1 p-0">
            {links.map((l) => (
              <li key={l.href}>
                <a
                  href={l.href}
                  onClick={() => close(false)}
                  className="flex min-h-14 items-center font-display text-[clamp(32px,9vw,48px)] font-extrabold leading-none tracking-[-0.02em] hover:text-pink-deep"
                >
                  {l.label}
                </a>
              </li>
            ))}
          </ul>
          <LangSwitch locale={locale} t={t} large />
          <a href="#booking" onClick={() => close(false)} className={`${btnPrimary} self-start`}>
            {t.book}
          </a>
        </nav>
      </div>
    </header>
  );
}
