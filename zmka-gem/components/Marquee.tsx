import type { Messages } from "@/lib/i18n";
import { Diamond } from "@/components/ui";

function Row({ items, hidden = false }: { items: string[]; hidden?: boolean }) {
  return (
    <ul aria-hidden={hidden || undefined} className="m-0 flex list-none p-0">
      {items.map((m) => (
        <li key={m} className="flex items-center gap-14 px-7">
          {m}
          <Diamond className="bg-magenta" />
        </li>
      ))}
    </ul>
  );
}

/** Ticker between two ink rules; pauses on hover/focus, the copy is aria-hidden. */
export function Marquee({ t }: { t: Messages["marquee"] }) {
  return (
    <div
      role="region"
      aria-label={t.label}
      tabIndex={0}
      className="marquee overflow-hidden border-y-[1.5px] border-ink bg-white py-[18px]"
    >
      <div className="marquee-track flex w-max flex-nowrap whitespace-nowrap font-display text-base font-semibold sm:text-lg">
        <Row items={t.items} />
        <Row items={t.items} hidden />
      </div>
    </div>
  );
}
