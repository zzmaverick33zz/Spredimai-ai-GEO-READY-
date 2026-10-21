"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { format, type Locale, type Messages } from "@/lib/i18n";
import { container, h2Class } from "@/components/ui";
import { site } from "@/content/site";

type Status = "idle" | "sending" | "success" | "error";
type FieldErrors = Partial<Record<"name" | "contact", string>>;
const TYPES = ["appointment", "training", "event"] as const;

const label = "flex flex-col gap-1.5 text-[13px] font-semibold";
const input =
  "w-full rounded-[14px] border-[1.5px] border-ink bg-white px-4 py-3.5 text-base font-normal text-ink placeholder:text-[#767676] aria-[invalid=true]:border-pink-deep";

export function Booking({ locale, t }: { locale: Locale; t: Messages["booking"] }) {
  const f = t.form;
  const [status, setStatus] = useState<Status>("idle");
  const [errors, setErrors] = useState<FieldErrors>({});
  const [type, setType] = useState<(typeof TYPES)[number]>("appointment");
  const nameRef = useRef<HTMLInputElement>(null);
  const contactRef = useRef<HTMLInputElement>(null);

  // Links like <a data-booking-type="training"> preselect the request type.
  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      const a = (e.target as Element | null)?.closest<HTMLElement>("[data-booking-type]");
      const v = a?.dataset.bookingType;
      if (v && (TYPES as readonly string[]).includes(v)) setType(v as (typeof TYPES)[number]);
    };
    document.addEventListener("click", onClick);
    // No-JS fallback: the API redirects back with ?sent=1 or ?sent=0.
    const sent = new URLSearchParams(window.location.search).get("sent");
    if (sent === "1") setStatus("success");
    if (sent === "0") setStatus("error");
    return () => document.removeEventListener("click", onClick);
  }, []);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const data = Object.fromEntries(new FormData(form)) as Record<string, string>;

    const next: FieldErrors = {};
    if (!data.name?.trim()) next.name = f.errors.name;
    if (!data.contact?.trim()) next.contact = f.errors.contact;
    setErrors(next);
    if (next.name) return nameRef.current?.focus();
    if (next.contact) return contactRef.current?.focus();

    setStatus("sending");
    try {
      const res = await fetch("/api/booking", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...data, locale }),
      });
      if (!res.ok) throw new Error(String(res.status));
      setStatus("success");
      form.reset();
      setType("appointment");
    } catch {
      setStatus("error");
    }
  }

  const statusText =
    status === "sending" ? f.sending : status === "success" ? f.success : status === "error" ? f.error : "";

  return (
    <section id="booking" aria-labelledby="booking-title" className={`${container} pb-10 pt-24`}>
      <div className="grid grid-cols-1 items-start gap-14 lg:grid-cols-2">
        <div className="flex min-w-0 flex-col gap-8">
          <h2 id="booking-title" className={h2Class}>
            {t.title}
          </h2>
          <ol className="m-0 flex list-none flex-col gap-5 p-0">
            {t.steps.map((st, i) => (
              <li key={st.title} className="flex items-start gap-[18px]">
                <span
                  aria-hidden="true"
                  className="flex size-11 flex-none items-center justify-center rounded-xl bg-ink font-display text-sm font-semibold text-white"
                >
                  {i + 1}
                </span>
                <div>
                  <h3 className="m-0 text-[17px] font-semibold">{st.title}</h3>
                  <p className="m-0 mt-1 text-[15px] leading-relaxed text-gray-text">{st.text}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>

        <form
          action="/api/booking"
          method="post"
          noValidate
          onSubmit={onSubmit}
          aria-labelledby="booking-form-title"
          className="relative flex min-w-0 flex-col gap-[18px] rounded-[28px] border-[1.5px] border-ink bg-white p-6 shadow-[8px_8px_0_0_var(--color-magenta)] sm:p-9"
        >
          <h3 id="booking-form-title" className="m-0 font-display text-xl font-semibold">
            {f.title}
          </h3>
          <input type="hidden" name="locale" value={locale} />
          {/* Honeypot: real people never see or fill this. */}
          <div aria-hidden="true" className="absolute -left-[9999px] h-px w-px overflow-hidden">
            <label>
              Company
              <input type="text" name="company" tabIndex={-1} autoComplete="off" />
            </label>
          </div>

          <label className={label}>
            {f.name}
            <input
              ref={nameRef}
              className={input}
              type="text"
              name="name"
              autoComplete="name"
              required
              aria-invalid={errors.name ? true : undefined}
              aria-describedby={errors.name ? "err-name" : undefined}
            />
            {errors.name && (
              <span id="err-name" className="text-[13px] font-medium text-pink-deep">
                {errors.name}
              </span>
            )}
          </label>

          <label className={label}>
            {f.contact}
            <input
              ref={contactRef}
              className={input}
              type="text"
              name="contact"
              autoComplete="off"
              spellCheck={false}
              required
              placeholder={f.contactPlaceholder}
              aria-invalid={errors.contact ? true : undefined}
              aria-describedby={errors.contact ? "err-contact" : undefined}
            />
            {errors.contact && (
              <span id="err-contact" className="text-[13px] font-medium text-pink-deep">
                {errors.contact}
              </span>
            )}
          </label>

          <label className={`${label} relative`}>
            {f.type}
            <select
              className={`${input} appearance-none pr-11`}
              name="type"
              value={type}
              onChange={(e) => setType(e.target.value as (typeof TYPES)[number])}
            >
              {TYPES.map((v) => (
                <option key={v} value={v}>
                  {f.types[v]}
                </option>
              ))}
            </select>
            <svg
              aria-hidden="true"
              width="12"
              height="8"
              viewBox="0 0 12 8"
              shapeRendering="crispEdges"
              className="pointer-events-none absolute bottom-[22px] right-[18px]"
            >
              <path d="M0 0h2v2H0zM2 2h2v2H2zM4 4h4v2H4zM8 2h2v2H8zM10 0h2v2h-2zM5 6h2v2H5z" fill="currentColor" />
            </svg>
          </label>

          <label className={label}>
            <span>
              {f.date} <span className="font-normal text-gray-soft">({f.optional})</span>
            </span>
            <input className={input} type="text" name="date" autoComplete="off" placeholder={f.datePlaceholder} />
          </label>

          <label className={label}>
            <span>
              {f.idea} <span className="font-normal text-gray-soft">({f.optional})</span>
            </span>
            <textarea className={`${input} resize-y`} name="idea" rows={3} placeholder={f.ideaPlaceholder} />
          </label>

          <button
            type="submit"
            disabled={status === "sending"}
            className="btn-pixel min-h-11 cursor-pointer rounded-full border-0 bg-ink px-7 py-[18px] text-base font-semibold text-white disabled:cursor-wait disabled:opacity-70"
          >
            {status === "sending" ? f.sending : f.submit}
          </button>

          <p
            role="status"
            aria-live="polite"
            className={`m-0 min-h-5 text-sm font-semibold ${status === "error" ? "text-pink-deep" : "text-ink"}`}
          >
            {statusText}
          </p>
          <p className="m-0 text-[13px] leading-normal text-gray-soft">{format(f.note, { deposit: site.deposit })}</p>
        </form>
      </div>
    </section>
  );
}
