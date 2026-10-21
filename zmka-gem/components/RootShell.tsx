import type { ReactNode } from "react";
import { poppins, unbounded } from "@/lib/fonts";
import type { Locale } from "@/lib/i18n";
import "@/app/globals.css";

export function RootShell({ locale, children }: { locale: Locale; children: ReactNode }) {
  return (
    <html lang={locale} className={`${unbounded.variable} ${poppins.variable}`}>
      <body>{children}</body>
    </html>
  );
}
