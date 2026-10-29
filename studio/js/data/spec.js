/* Specification data for "Specify it with confidence". EDIT THIS FILE to change what architects see; the page renders from it.
   tbc: true = the value comes from the design mock-up and has not been confirmed by Big Foot Floors yet (shown with a "TBC" mark).
   When every value is confirmed, set  confirmed: true  and the marks disappear. */
window.BFF_SPEC = {
  confirmed: false,
  species: [
    { id: 'bog-oak', name: 'Bog oak', ancient: true, note: 'The signature. Famous for its wide natural colour palette and intricate grain.', colour: 'Honey-brown to nearly black' },
    { id: 'bog-ash', name: 'Bog ash', ancient: true, note: 'Rich, deep colours and intricate, unique grain patterns.', colour: 'Rich, deep tones' },
    { id: 'black-walnut', name: 'Black walnut', note: 'A forest species for broken geometric patterns and warm tones.' },
    { id: 'elm', name: 'Elm', note: 'A forest species with golden, flowing grain.' },
    { id: 'oak', name: 'Oak', note: 'A forest species, from planks to sunburst patterns.' },
    { id: 'ash', name: 'Ash', note: 'A forest species with pale, flowing grain.' }
  ],
  rows: [
    { k: 'Construction', v: 'Multilayer board' },
    { k: 'Stability', v: 'Stable with changes in temperature and humidity' },
    { k: 'Underfloor heating', v: 'Compatible' },
    { k: 'Origin', v: 'Lakes and peat bogs. The trees were never felled and are carbon-dated.', only: 'ancient' },
    { k: 'Origin', v: 'Forest species', only: 'forest' },
    { k: 'Colour', v: '{colour}', only: 'ancient' },
    { k: 'Board width', v: '180–300 mm', tbc: true },
    { k: 'Wear layer', v: '4 or 6 mm', tbc: true },
    { k: 'Board length', v: '1,200–2,400 mm', tbc: true },
    { k: 'Finish', v: 'Oil, hardwax oil or matt lacquer', tbc: true },
    { k: 'Made in', v: 'Our workshop in Lithuania' },
    { k: 'Installation', v: 'By our own craftsmen, worldwide' },
    { k: 'Aftercare', v: 'Care guidance, repair and refresh' }
  ],
  docs: [
    { id: 'datasheet', label: 'Technical datasheet', kind: 'PDF' },
    { id: 'installation', label: 'Installation guide', kind: 'PDF' },
    { id: 'cad', label: 'CAD / BIM files', kind: 'DWG · RVT' },
    { id: 'textures', label: 'Texture pack', kind: 'JPG' },
    { id: 'dating', label: 'Carbon-dating protocol', kind: 'PDF' }
  ]
};
