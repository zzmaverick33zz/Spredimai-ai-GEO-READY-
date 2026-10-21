import Image from "next/image";
import type { Locale, Messages } from "@/lib/i18n";
import { services } from "@/content/services";
import { training } from "@/content/training";
import { site } from "@/content/site";
import { Butterfly, DitherButterfly, Sprite } from "@/components/Butterfly";
import { Diamond, ExternalLink, btnOutline, btnPrimary, container, h2Class } from "@/components/ui";

export function Services({ locale, t }: { locale: Locale; t: Messages["services"] }) {
  return (
    <section id="services" aria-labelledby="services-title" className={`${container} pb-10 pt-24`}>
      <h2 id="services-title" className={`${h2Class} mb-12`}>
        {t.title}
      </h2>
      <ul className="m-0 grid list-none grid-cols-[repeat(auto-fit,minmax(min(260px,100%),1fr))] gap-6 p-0">
        {services.map((s) => {
          const item = t.items[s.id];
          return (
            <li
              key={s.id}
              className="flex flex-col gap-3.5 rounded-[24px] border-[1.5px] border-ink bg-white p-7"
            >
              <span aria-hidden="true" className="font-display text-[13px] font-semibold text-pink-deep">
                {s.n}
              </span>
              <h3 className="m-0 font-display text-[22px] font-semibold leading-tight">{item.title}</h3>
              <p className="m-0 grow text-[15px] leading-relaxed text-gray-text">{item.text}</p>
              <p className="m-0 text-[15px] font-semibold">{s.price[locale]}</p>
            </li>
          );
        })}
      </ul>
    </section>
  );
}

export function Why({ t }: { t: Messages["why"] }) {
  return (
    <section aria-labelledby="why-title" className={`${container} pb-10 pt-24`}>
      <div className="relative flex flex-wrap items-center gap-10 overflow-hidden rounded-[32px] bg-blush px-6 py-12 sm:px-12 sm:py-14">
        <div className="dither-dense opacity-25" />
        <h2
          id="why-title"
          className="relative m-0 flex-[1_1_300px] font-display text-[clamp(30px,3.6vw,48px)] font-extrabold leading-[1.08] tracking-[-0.02em]"
        >
          {t.titleA} <span className="text-pink-deep">{t.titleAccent}</span>
        </h2>
        <ul className="relative m-0 grid flex-[2_1_460px] list-none grid-cols-1 sm:grid-cols-2 gap-5 p-0">
          {t.items.map((y) => (
            <li key={y} className="flex flex-col gap-2.5 rounded-[20px] bg-white p-[22px]">
              <Diamond size={14} className="bg-magenta" />
              {/*   keeps "100% safe" on one line */}
              <span className="text-base font-semibold leading-snug">{y.replace("% ", "% ")}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

export function Training({ locale, t, newTab }: { locale: Locale; t: Messages["training"]; newTab: string }) {
  if (!site.sections.training) return null;
  const facts = (Object.keys(training.facts) as (keyof typeof training.facts)[]).map((k) => ({
    k,
    label: t.facts[k],
    value: training.facts[k][locale],
  }));
  return (
    <section id="training" aria-labelledby="training-title" className={`${container} pb-10 pt-24`}>
      <div className="grid grid-cols-1 items-start gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:gap-14">
        <div className="relative order-2 lg:order-1">
          <div className="relative overflow-hidden rounded-[32px] border-[1.5px] border-ink shadow-[8px_8px_0_0_var(--color-magenta)]">
            <Image
              src={training.photo.src}
              alt={t.photoAlt}
              width={training.photo.width}
              height={training.photo.height}
              sizes="(min-width: 1024px) 480px, 100vw"
              className="block aspect-[4/5] h-auto w-full object-cover"
            />
          </div>
          <Butterfly drift="drift-3" flap="flap-slow" className="-right-3 -top-8 sm:-right-6">
            <Sprite size={48} scale={1} />
          </Butterfly>
        </div>

        <div className="order-1 flex min-w-0 flex-col gap-7 lg:order-2">
          <p className="m-0 inline-flex items-center gap-2.5 self-start rounded-full border-[1.5px] border-ink px-4 py-2 text-[13px] font-medium">
            <span aria-hidden="true" className="block size-2 bg-magenta" />
            {t.eyebrow}
          </p>
          <h2 id="training-title" className={h2Class}>
            {t.title}
          </h2>
          <p className="m-0 max-w-[560px] text-[17px] leading-relaxed text-gray-text">{t.lead}</p>

          <div>
            <h3 className="m-0 mb-4 font-display text-lg font-semibold">{t.programTitle}</h3>
            <ul className="m-0 grid list-none grid-cols-[repeat(auto-fit,minmax(min(240px,100%),1fr))] gap-x-6 gap-y-3 p-0">
              {t.program.map((p) => (
                <li key={p} className="flex items-start gap-3 text-[15px] leading-snug">
                  <Diamond className="mt-1.5 bg-magenta" />
                  {p}
                </li>
              ))}
            </ul>
          </div>

          <dl className="m-0 grid grid-cols-2 gap-3 sm:grid-cols-4">
            {facts.map((f) => (
              <div key={f.k} className="flex flex-col gap-1 rounded-[20px] bg-blush p-4">
                <dt className="text-xs font-semibold text-gray-soft">{f.label}</dt>
                <dd className="m-0 text-sm font-semibold">{f.value}</dd>
              </div>
            ))}
          </dl>

          <div className="flex flex-col gap-4 sm:flex-row sm:flex-wrap">
            <a href="#booking" data-booking-type="training" className={btnPrimary}>
              {t.cta}
            </a>
            <ExternalLink href={site.instagramDm} newTabLabel={newTab} className={btnOutline}>
              {t.dm}
            </ExternalLink>
          </div>
        </div>
      </div>
    </section>
  );
}

export function Events({ t, newTab }: { t: Messages["events"]; newTab: string }) {
  return (
    <section id="events" aria-labelledby="events-title" className={`${container} pb-24 pt-24`}>
      <div className="relative flex flex-wrap items-center gap-8 overflow-hidden rounded-[32px] bg-ink px-6 py-14 text-white sm:px-12 sm:py-16">
        <div className="dither-light opacity-30" />
        <div className="relative flex flex-[1_1_380px] flex-col gap-5">
          <h2
            id="events-title"
            className="m-0 font-display text-[clamp(30px,3.6vw,48px)] font-extrabold leading-[1.08] tracking-[-0.02em]"
          >
            {t.title}
          </h2>
          <p className="m-0 max-w-[460px] text-[17px] leading-relaxed text-[#e8e8e8]">{t.text}</p>
          <ExternalLink
            href={site.instagramDm}
            newTabLabel={newTab}
            className="btn-pixel inline-flex min-h-11 items-center self-start rounded-full bg-white px-7 py-4 font-semibold text-ink"
          >
            {t.cta}
          </ExternalLink>
        </div>
        <div className="relative h-[220px] flex-[1_1_280px] sm:h-[260px]">
          <Butterfly drift="drift-3" flap="flap-slow" className="left-1/2 top-1/2 -ml-[110px] -mt-[120px] w-[220px] sm:-ml-[120px] sm:-mt-[130px] sm:w-[240px]">
            <DitherButterfly size={240} light />
          </Butterfly>
          <span aria-hidden="true" className="diamond twinkle absolute left-[14%] top-[18%] block size-4 bg-magenta" />
          <span
            aria-hidden="true"
            className="diamond twinkle absolute bottom-[12%] right-[16%] block size-3 bg-white"
            style={{ animationDelay: "1s" }}
          />
        </div>
      </div>
    </section>
  );
}

/** Hidden until real reviews exist (site.sections.feedback). */
export function Feedback({ t }: { t: Messages["feedback"] }) {
  if (!site.sections.feedback) return null;
  return (
    <section id="feedback" aria-labelledby="feedback-title" className={`${container} pb-10 pt-24`}>
      <h2 id="feedback-title" className={h2Class}>
        {t.title}
      </h2>
    </section>
  );
}

/** Hidden until warranty terms are written (site.sections.warranty). */
export function Warranty({ t }: { t: Messages["warranty"] }) {
  if (!site.sections.warranty) return null;
  return (
    <section id="warranty" aria-labelledby="warranty-title" className={`${container} pb-10 pt-24`}>
      <h2 id="warranty-title" className={h2Class}>
        {t.title}
      </h2>
    </section>
  );
}
