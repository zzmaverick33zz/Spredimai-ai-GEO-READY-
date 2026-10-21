/**
 * Portfolio. Photos live in /public/work (built by scripts/prepare_assets.py).
 * Set `src: null` to show a blush placeholder for a slot.
 */
export type WorkItem = {
  label: string;
  src: string | null;
  width: number;
  height: number;
  /** Tile shape in the grid; the photo is cropped to it. */
  ratio: "4 / 5" | "1 / 1";
  alt: { en: string; lt: string };
};

export const work: WorkItem[] = [
  {
    label: "set 01",
    src: "/work/set-01.jpg",
    width: 1360,
    height: 1600,
    ratio: "4 / 5",
    alt: {
      en: "Upper teeth covered in colourful crystals: a blue flower, violet marquise stones, stars and round pink and green gems",
      lt: "Viršutiniai dantys su spalvotais kristalais: mėlyna gėlė, violetiniai markizo akmenys, žvaigždės, rožiniai ir žali kristalai",
    },
  },
  {
    label: "set 02",
    src: "/work/set-02.jpg",
    width: 1200,
    height: 1600,
    ratio: "1 / 1",
    alt: {
      en: "Two pink heart crystals on the front teeth with small clear gems along the smile",
      lt: "Du rožiniai širdelės kristalai ant priekinių dantų ir smulkūs skaidrūs kristalai šypsenoje",
    },
  },
  {
    label: "set 03",
    src: "/work/set-03.jpg",
    width: 1201,
    height: 1600,
    ratio: "4 / 5",
    alt: {
      en: "Profile smile with a pink star crystal, round pink, green and blue gems and a clear marquise stone",
      lt: "Šypsena iš šono: rožinė žvaigždė, apvalūs rožiniai, žali ir mėlyni kristalai bei skaidrus markizo akmuo",
    },
  },
  {
    label: "set 04",
    src: "/work/set-04.jpg",
    width: 960,
    height: 1280,
    ratio: "1 / 1",
    alt: {
      en: "Gold leaf-shaped crystals mirrored on the two front teeth",
      lt: "Auksiniai lapelio formos kristalai, simetriškai ant dviejų priekinių dantų",
    },
  },
  {
    label: "set 05",
    src: "/work/set-05.jpg",
    width: 1200,
    height: 1600,
    ratio: "4 / 5",
    alt: {
      en: "Side view of a smile with clear and pink marquise and round crystals on the front teeth",
      lt: "Šypsena iš šono su skaidriais ir rožiniais markizo bei apvaliais kristalais",
    },
  },
  {
    label: "set 06",
    src: "/work/set-06.jpg",
    width: 960,
    height: 1280,
    ratio: "1 / 1",
    alt: {
      en: "A mix of clear diamond shapes and blue, green and red round gems across the upper teeth",
      lt: "Skaidrūs rombo formos kristalai ir mėlyni, žali bei raudoni apvalūs kristalai ant viršutinių dantų",
    },
  },
];
