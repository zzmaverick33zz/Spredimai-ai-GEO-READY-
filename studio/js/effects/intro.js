/* Premium intro: brass growth rings draw while the page settles, then the curtain lifts. Runs once per session.
   Transform / opacity / stroke-dashoffset only. Skipped for reduced motion, ?static and repeat visits. */
(function () {
  'use strict';
  const el = document.getElementById('preloader');
  const skip = !el || BFF.reduce || (function () { try { return sessionStorage.getItem('bff-intro') === '1'; } catch (_) { return false; } })();
  BFF.introDelay = 0;
  document.body.classList.add('js-ready');
  if (skip) { if (el) el.remove(); return; }
  document.documentElement.classList.add('has-intro');
  const NS = 'http://www.w3.org/2000/svg', svg = el.querySelector('svg'); let seed = 11;
  const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647, paths = [];
  for (let k = 0; k < 14; k++) {                                           // irregular concentric rings, like a cut trunk
    const r0 = 9 + k * 6.4, ph = rnd() * 6.28, pts = [];
    for (let i = 0; i < 72; i++) { const a = (i / 72) * 6.2832, r = r0 + Math.sin(a * 3 + ph) * (0.6 + k * 0.14) + Math.sin(a * 5 + ph * 1.7) * (0.4 + k * 0.1); pts.push((100 + Math.cos(a) * r).toFixed(1) + ' ' + (100 + Math.sin(a) * r * 0.94).toFixed(1)); }
    const p = document.createElementNS(NS, 'path'); p.setAttribute('d', 'M' + pts.join('L') + 'Z'); p.setAttribute('pathLength', '1'); p.setAttribute('stroke-opacity', String(0.75 - k * 0.04));
    p.style.strokeDasharray = '1'; p.style.strokeDashoffset = '1'; svg.append(p); paths.push(p);
  }
  BFF.introDelay = 1.05;
  const g = window.gsap, done = () => { document.documentElement.classList.remove('has-intro'); el.remove(); try { sessionStorage.setItem('bff-intro', '1'); } catch (_) {} };
  if (!g) { done(); return; }
  g.timeline({ onComplete: done })
    .to(paths, { strokeDashoffset: 0, duration: 1.1, ease: 'power2.inOut', stagger: 0.05 }, 0)
    .from('.intro__mark, .intro__sub', { opacity: 0, y: 8, duration: 0.6, stagger: 0.1, ease: 'power2.out' }, 0.4)
    .to(el, { yPercent: -100, duration: 0.9, ease: 'power3.inOut' }, 1.55)
    .to(svg, { scale: 1.25, opacity: 0, duration: 0.6, ease: 'power2.in' }, 1.5);
})();
