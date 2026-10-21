import type { MetadataRoute } from "next";
import { site } from "@/content/site";

export default function sitemap(): MetadataRoute.Sitemap {
  const languages = { en: `${site.url}/`, lt: `${site.url}/lt` };
  return [
    { url: `${site.url}/`, alternates: { languages } },
    { url: `${site.url}/lt`, alternates: { languages } },
  ];
}
