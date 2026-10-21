/**
 * Everything that still needs the artist's confirmation lives here.
 * Values in [brackets] are placeholders and are shown on the site as is.
 */
export const site = {
  name: "ZM_KA GEM",
  handle: "@zm_ka_gem",
  artistHandle: "@zm_ka",
  url: process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000",
  city: "Vilnius",
  country: "LT",

  instagram: "https://instagram.com/zm_ka_gem",
  instagramDm: "https://ig.me/m/zm_ka_gem",

  // Placeholders — replace when confirmed.
  address: "[STUDIO ADDRESS]",
  phone: "[PHONE]",
  deposit: "[DEPOSIT €]",

  /** Set an address here only once it is confirmed; it then goes into JSON-LD. */
  confirmedAddress: null as null | { street: string; postalCode: string },

  /** Section flags: hidden sections stay in the code with their anchors. */
  sections: {
    training: true,
    feedback: false, // turn on only with real reviews
    warranty: false, // turn on once warranty terms are written
  },
} as const;
