/* Radiocarbon results shown on the page (chapter IV and "The material"). EDIT THIS FILE to update them; nothing else needs touching.
   The page is universal (many species, many trunks): these are examples from the latest laboratory protocol, not a claim about every board.
   bp = radiocarbon age in years before 1950, err = laboratory uncertainty (±), cal = calibrated range as printed in the protocol (optional). */
window.BFF_SAMPLES = {
  scaleMax: 3600,
  source: 'Radiocarbon protocol BGRL-357, Nature Research Centre, Vilnius, issued 9 December 2025. Method: liquid scintillation beta spectrometry; calibration OxCal 4.4, IntCal2020.',
  samples: [
    { species: 'Oak', id: '2025-1/TN',  bp: 3334, err: 93, cal: '3775–3375 cal BP (95.4%)' },
    { species: 'Ash', id: 'Andrius-1',  bp: 1108, err: 50, cal: '1180–925 cal BP (95.4%)' },
    { species: 'Guoba', id: '2025-1/TN', bp: 595, err: 45, cal: '655–530 cal BP (95.4%)' },
    { species: 'Ash', id: 'Marijanė-1', bp: 274,  err: 63, cal: '495–140 cal BP (95.4%)' }
  ]
};
