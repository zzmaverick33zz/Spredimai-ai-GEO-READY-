import en from "@/messages/en.json";
import lt from "@/messages/lt.json";

export const locales = ["en", "lt"] as const;
export type Locale = (typeof locales)[number];
export type Messages = typeof en;

const dictionaries: Record<Locale, Messages> = { en, lt };

export function getMessages(locale: Locale): Messages {
  return dictionaries[locale];
}

/** Home path for a locale: EN lives at "/", LT at "/lt". */
export function localePath(locale: Locale): string {
  return locale === "en" ? "/" : `/${locale}`;
}

export function format(template: string, values: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (_, key: string) => String(values[key] ?? `{${key}}`));
}
