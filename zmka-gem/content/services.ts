/** Prices are placeholders; texts live in messages/*.json under services.items.<id>. */
export const services = [
  { id: "single", n: "01", price: { en: "from [€ ]", lt: "nuo [€ ]" } },
  { id: "set", n: "02", price: { en: "from [€ ]", lt: "nuo [€ ]" } },
  { id: "freestyle", n: "03", price: { en: "from [€ ]", lt: "nuo [€ ]" } },
  { id: "events", n: "04", price: { en: "on request", lt: "pagal užklausą" } },
] as const;

export type ServiceId = (typeof services)[number]["id"];
