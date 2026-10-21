/**
 * Training (course) facts. Texts are in messages/*.json under training.*;
 * values in [brackets] are placeholders to confirm with the artist.
 */
export const training = {
  photo: { src: "/work/training.jpg", width: 1200, height: 1600 },
  facts: {
    format: { en: "[1:1 / small group]", lt: "[individualiai / maža grupė]" },
    duration: { en: "[HOURS / DAYS]", lt: "[VALANDOS / DIENOS]" },
    price: { en: "from [€ ]", lt: "nuo [€ ]" },
    next: { en: "[NEXT DATES]", lt: "[ARTIMIAUSIOS DATOS]" },
  },
} as const;
