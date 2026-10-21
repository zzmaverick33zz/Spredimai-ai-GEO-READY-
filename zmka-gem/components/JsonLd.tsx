import { site } from "@/content/site";
import type { Messages } from "@/lib/i18n";

export function JsonLd({ meta }: { meta: Messages["meta"] }) {
  const data = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    name: site.name,
    description: meta.description,
    url: site.url,
    image: `${site.url}/opengraph-image.png`,
    address: {
      "@type": "PostalAddress",
      addressLocality: site.city,
      addressCountry: site.country,
      ...(site.confirmedAddress
        ? { streetAddress: site.confirmedAddress.street, postalCode: site.confirmedAddress.postalCode }
        : {}),
    },
    sameAs: [site.instagram],
  };
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data).replace(/</g, "\\u003c") }}
    />
  );
}
