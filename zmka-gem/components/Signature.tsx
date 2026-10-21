import Image from "next/image";
import type { Messages } from "@/lib/i18n";
import { Sprite } from "@/components/Butterfly";
import { container } from "@/components/ui";
import { site } from "@/content/site";

/** Artist's signature: the work is by a person, not a salon. */
export function Signature({ t }: { t: Messages["signature"] }) {
  return (
    <div className={`${container} pt-20 sm:pt-28`}>
      <figure className="m-0 flex flex-col gap-5 border-l-[3px] border-magenta pl-5 sm:flex-row sm:items-center sm:justify-between sm:gap-10 sm:pl-8">
        <blockquote className="m-0 max-w-[620px] font-display text-[clamp(20px,2.2vw,28px)] font-semibold leading-snug tracking-[-0.01em]">
          {t.text}
        </blockquote>
        <figcaption className="flex shrink-0 items-center gap-4">
          <Sprite size={32} scale={1} />
          <span className="flex flex-col gap-1.5">
            <span className="text-sm text-gray-soft">
              {t.by}{" "}
              <span translate="no" className="font-semibold text-ink">
                {site.artistHandle}
              </span>
            </span>
            <Image
              src="/brand/wordmark-black.png"
              alt="ZM_KA GEM"
              translate="no"
              width={158}
              height={18}
              className="block h-[18px] w-auto"
              style={{ width: "auto" }}
            />
          </span>
        </figcaption>
      </figure>
    </div>
  );
}
