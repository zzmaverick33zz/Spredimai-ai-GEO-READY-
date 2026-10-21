import { NextResponse } from "next/server";

type Booking = {
  name: string;
  contact: string;
  type: string;
  date: string;
  idea: string;
  locale: string;
};

const TYPES: Record<string, string> = { appointment: "Appointment", training: "Training", event: "Event / collab" };
const MAX = { name: 120, contact: 160, date: 120, idea: 2000 };

function clean(v: unknown, max: number): string {
  return typeof v === "string" ? v.trim().slice(0, max) : "";
}

function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);
}

async function readBody(req: Request): Promise<{ data: Record<string, unknown>; isForm: boolean }> {
  const type = req.headers.get("content-type") || "";
  if (type.includes("application/json")) return { data: await req.json(), isForm: false };
  const fd = await req.formData();
  return { data: Object.fromEntries(fd), isForm: true };
}

function lines(b: Booking): string[] {
  return [
    `Name: ${b.name}`,
    `Contact: ${b.contact}`,
    `Request: ${TYPES[b.type] ?? b.type}`,
    `Preferred date: ${b.date || "—"}`,
    `Idea: ${b.idea || "—"}`,
    `Language: ${b.locale.toUpperCase()}`,
  ];
}

async function sendEmail(b: Booking): Promise<boolean> {
  const key = process.env.RESEND_API_KEY;
  const to = process.env.BOOKING_TO_EMAIL;
  if (!key || !to) return false;
  const from = process.env.BOOKING_FROM_EMAIL || "ZM_KA GEM <onboarding@resend.dev>";
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      from,
      to: to.split(",").map((s) => s.trim()),
      subject: `New ${TYPES[b.type] ?? "booking"} request — ${b.name}`,
      text: lines(b).join("\n"),
      html: `<h2 style="font-family:sans-serif">New request</h2><p style="font-family:sans-serif;line-height:1.6">${lines(b)
        .map(escapeHtml)
        .join("<br>")}</p>`,
    }),
  });
  if (!res.ok) throw new Error(`Resend ${res.status}: ${await res.text()}`);
  return true;
}

async function sendTelegram(b: Booking): Promise<boolean> {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chat = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chat) return false;
  const res = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id: chat, text: ["New request — ZM_KA GEM", "", ...lines(b)].join("\n") }),
  });
  if (!res.ok) throw new Error(`Telegram ${res.status}: ${await res.text()}`);
  return true;
}

export async function POST(req: Request) {
  let raw: Record<string, unknown>;
  let isForm = false;
  try {
    ({ data: raw, isForm } = await readBody(req));
  } catch {
    return NextResponse.json({ ok: false, error: "bad_request" }, { status: 400 });
  }

  const locale = raw.locale === "lt" ? "lt" : "en";
  const home = new URL(locale === "lt" ? "/lt" : "/", req.url);

  // Honeypot filled: pretend success, send nothing.
  if (clean(raw.company, 200)) {
    return isForm
      ? NextResponse.redirect(new URL(`${home.pathname}?sent=1#booking`, req.url), 303)
      : NextResponse.json({ ok: true });
  }

  const b: Booking = {
    name: clean(raw.name, MAX.name),
    contact: clean(raw.contact, MAX.contact),
    type: TYPES[clean(raw.type, 20)] ? clean(raw.type, 20) : "appointment",
    date: clean(raw.date, MAX.date),
    idea: clean(raw.idea, MAX.idea),
    locale,
  };
  if (!b.name || !b.contact) {
    return NextResponse.json({ ok: false, error: "missing_fields" }, { status: 422 });
  }

  const results = await Promise.allSettled([sendEmail(b), sendTelegram(b)]);
  const delivered = results.some((r) => r.status === "fulfilled" && r.value);
  results.forEach((r) => r.status === "rejected" && console.error("[booking]", r.reason));

  if (!delivered) {
    if (process.env.NODE_ENV !== "production") {
      // Local development without keys: log instead of failing.
      console.info("[booking] no channel configured, request:\n" + lines(b).join("\n"));
    } else {
      return isForm
        ? NextResponse.redirect(new URL(`${home.pathname}?sent=0#booking`, req.url), 303)
        : NextResponse.json({ ok: false, error: "not_delivered" }, { status: 502 });
    }
  }

  return isForm
    ? NextResponse.redirect(new URL(`${home.pathname}?sent=1#booking`, req.url), 303)
    : NextResponse.json({ ok: true });
}
