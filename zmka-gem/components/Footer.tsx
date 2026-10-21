import Image from "next/image";
import type { Messages } from "@/lib/i18n";
import { site } from "@/content/site";
import { MotionToggle } from "@/components/MotionToggle";
import { ExternalLink, container } from "@/components/ui";

export function Footer({ t, newTab }: { t: Messages["footer"]; newTab: string }) {
  return (
    <footer className="overflow-hidden border-t-[1.5px] border-ink">
      <div className={`${container} flex flex-wrap items-center justify-between gap-x-6 gap-y-4 py-8`}>
        <p className="m-0 text-sm text-gray-text">
          {t.city} · {site.address}
        </p>
        <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
          <MotionToggle pauseLabel={t.pause} playLabel={t.play} />
          <ExternalLink
            href={site.instagram}
            newTabLabel={newTab}
            className="inline-flex min-h-11 items-center text-sm font-semibold hover:text-pink-deep"
          >
            <span translate="no">{site.handle}</span>
          </ExternalLink>
        </div>
      </div>
      {/* Wordmark as graphics: full width, clipped at the bottom. */}
      <div className={`${container} relative`}>
        <div className="h-[calc((min(100vw,1240px)-32px)*0.088)] overflow-hidden sm:h-[calc((min(100vw,1240px)-64px)*0.088)]">
          <Image
            src="/brand/wordmark-black.png"
            alt="ZM_KA GEM"
            translate="no"
            width={1600}
            height={182}
            sizes="(min-width: 1240px) 1176px, 100vw"
            className="block h-auto w-full"
          />
        </div>
      </div>
    </footer>
  );
}
