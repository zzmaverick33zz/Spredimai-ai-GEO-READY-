import type { Metadata, Viewport } from "next";
import { site } from "@/content/site";
import { getMessages, localePath, type Locale } from "@/lib/i18n";

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#ffffff",
  colorScheme: "light",
};

export function buildMetadata(locale: Locale): Metadata {
  const m = getMessages(locale).meta;
  return {
    metadataBase: new URL(site.url),
    title: m.title,
    description: m.description,
    alternates: {
      canonical: localePath(locale),
      languages: { en: "/", lt: "/lt", "x-default": "/" },
    },
    openGraph: {
      type: "website",
      siteName: site.name,
      title: m.title,
      description: m.description,
      url: localePath(locale),
      locale: locale === "en" ? "en_US" : "lt_LT",
    },
    twitter: { card: "summary_large_image", title: m.title, description: m.description },
  };
}
