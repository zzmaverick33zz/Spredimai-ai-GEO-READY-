import type { ReactNode } from "react";
import { RootShell } from "@/components/RootShell";
import { buildMetadata } from "@/lib/metadata";

export { viewport } from "@/lib/metadata";
export const metadata = buildMetadata("lt");

export default function Layout({ children }: { children: ReactNode }) {
  return <RootShell locale="lt">{children}</RootShell>;
}
