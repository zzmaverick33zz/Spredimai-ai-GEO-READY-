/* Premium extras: custom cursor ring, chapter numerals that drift, decorative contour lines in "The dive".
   Everything is transform / opacity; nothing repaints while scrolling. */
(function () {
  'use strict';
  const { $, $$ } = BFF;

  function numerals() {
    if (BFF.reduce || !window.gsap) return;
    $$('.chapter .numeral').forEach((n) => window.gsap.fromTo(n, { yPercent: 14 }, { yPercent: -14, ease: 'none', scrollTrigger: { trigger: n.closest('.chapter'), start: 'top bottom', end: 'bottom top', scrub: true } }));
  }

  function contours() {
    const host = $('#ch2'); if (!host || BFF.reduce) return;
    const NS = 'http://www.w3.org/2000/svg', svg = document.createElementNS(NS, 'svg'); svg.setAttribute('class', 'contours'); svg.setAttribute('viewBox', '0 0 1000 700'); svg.setAttribute('preserveAspectRatio', 'xMidYMid slice'); svg.setAttribute('aria-hidden', 'true');
    let seed = 5; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647, paths = [];
    for (let k = 0; k < 9; k++) {
      const r0 = 60 + k * 46, ph = rnd() * 6.28, pts = [];
      for (let i = 0; i < 90; i++) { const a = (i / 90) * 6.2832, r = r0 + Math.sin(a * 2 + ph) * (14 + k * 5) + Math.sin(a * 5 + ph * 2) * (6 + k * 2); pts.push((620 + Math.cos(a) * r * 1.5).toFixed(1) + ' ' + (330 + Math.sin(a) * r * 0.8).toFixed(1)); }
      const p = document.createElementNS(NS, 'path'); p.setAttribute('d', 'M' + pts.join('L') + 'Z'); p.setAttribute('pathLength', '1'); p.style.strokeDasharray = '1'; p.style.strokeDashoffset = '1'; svg.append(p); paths.push(p);
    }
    host.prepend(svg);
    window.ScrollTrigger.create({ trigger: host, start: 'top 75%', once: true, onEnter: () => window.gsap.to(paths, { strokeDashoffset: 0, duration: 2.4, ease: 'power2.out', stagger: 0.12 }) });
  }

  BFF.fx.extras = { init() { numerals(); contours(); } };
})();
