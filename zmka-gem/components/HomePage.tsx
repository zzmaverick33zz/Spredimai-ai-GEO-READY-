import { getMessages, type Locale } from "@/lib/i18n";
import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { Marquee } from "@/components/Marquee";
import { Signature } from "@/components/Signature";
import { Work } from "@/components/Work";
import { Events, Feedback, Services, Training, Warranty, Why } from "@/components/Sections";
import { Booking } from "@/components/Booking";
import { Footer } from "@/components/Footer";
import { Reveal } from "@/components/Reveal";
import { CursorTrail } from "@/components/CursorTrail";
import { ScrollButterflies } from "@/components/ScrollButterflies";
import { JsonLd } from "@/components/JsonLd";

export function HomePage({ locale }: { locale: Locale }) {
  const t = getMessages(locale);
  return (
    <>
      <a className="skip-link" href="#main">
        {t.skip}
      </a>
      <Header locale={locale} t={t.nav} />
      <main id="main" className="overflow-x-clip">
        <Hero t={t.hero} />
        <Marquee t={t.marquee} />
        <Reveal>
          <Signature t={t.signature} />
        </Reveal>
        <Reveal>
          <Work locale={locale} t={t.work} newTab={t.external} />
        </Reveal>
        <Reveal>
          <Services locale={locale} t={t.services} />
        </Reveal>
        <Reveal>
          <Why t={t.why} />
        </Reveal>
        <Reveal>
          <Training locale={locale} t={t.training} newTab={t.external} />
        </Reveal>
        <Feedback t={t.feedback} />
        <Reveal>
          <Booking locale={locale} t={t.booking} />
        </Reveal>
        <Warranty t={t.warranty} />
        <Reveal>
          <Events t={t.events} newTab={t.external} />
        </Reveal>
      </main>
      <Footer t={t.footer} newTab={t.external} />
      <ScrollButterflies />
      <CursorTrail />
      <JsonLd meta={t.meta} />
    </>
  );
}
