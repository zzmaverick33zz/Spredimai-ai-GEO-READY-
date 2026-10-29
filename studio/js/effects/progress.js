/* Effect 6: shared scroll progress, depth gauge, growth rings.
   Progress line: the existing .rail line (already driven in app.js) gains a brass head dot and the gauge below.
   Style reference: 21st.dev "Scroll animated timeline" (ibrandify, MIT: a progress line that draws on scroll). Its source needs an
   API key and could not be read; the draw logic here is the page's own scroll progress.
   Depth gauge and growth rings are custom (no 21st.dev equivalent).
   Depth gauge: RELATIVE only (surface -> deep -> surface). No real lake depth is stated anywhere; the placeholder
   depths live in data-depth on each chapter as TODO values: confirm with client before showing metres.
   Growth rings: concentric irregular circles drawn with stroke-dashoffset over the cross-section (S08). */
(function () {
  'use strict';
  const { $, $$, clamp } = BFF;

  // relative depth per chapter, 0 = surface, 1 = deepest. TODO: confirm with client (never shown as metres)
  const DEPTH = { ch1: 0.55, ch2: 1, ch3: 0, ch4: 0, ch5: 0, ch6: 0, ch7: 0, ch8: 0 };

  function gauge() {
    const rail = $('#rail'); if (!rail) return null;
    const g = document.createElement('div'); g.className = 'rail__depth'; g.setAttribute('aria-hidden', 'true');
    g.innerHTML = '<span class="rail__depth-k">Surface</span><span class="rail__depth-track"><i></i></span><span class="rail__depth-k">Deep</span><span class="rail__depth-todo todo-only">TODO: confirm depth in metres with client</span>';
    rail.append(g);
    return { dot: $('i', g), g };
  }

  function depthAt(y) {                                                           // interpolate between chapter centres
    const pts = Object.keys(DEPTH).map((id) => { const e = document.getElementById(id); if (!e) return null; const r = e.getBoundingClientRect(); return { y: r.top + window.scrollY + r.height / 2, d: DEPTH[id] }; }).filter(Boolean);
    if (!pts.length) return 0;
    if (y <= pts[0].y) return pts[0].d * clamp((y - (pts[0].y - 400)) / 400, 0, 1);
    for (let i = 1; i < pts.length; i++) if (y <= pts[i].y) { const a = pts[i - 1], b = pts[i]; return a.d + (b.d - a.d) * ((y - a.y) / (b.y - a.y)); }
    return 0;
  }

  function rings(still) {
    const slot = document.querySelector('[data-slot="S08"]'); if (!slot) return;
    const NS = 'http://www.w3.org/2000/svg', svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('viewBox', '0 0 200 200'); svg.setAttribute('class', 'rings'); svg.setAttribute('aria-hidden', 'true'); svg.setAttribute('preserveAspectRatio', 'xMidYMid slice');
    let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;       // deterministic: same rings on every load
    const paths = [];
    for (let k = 0; k < 15; k++) {
      const r0 = 7 + k * 5.4, ph = rnd() * 6.28, pts = [];
      for (let i = 0; i < 64; i++) { const a = (i / 64) * 6.2832, r = r0 + Math.sin(a * 3 + ph) * (0.8 + k * 0.16) + Math.sin(a * 5 + ph * 1.7) * (0.5 + k * 0.1); pts.push([96 + 3 * (k / 15) + Math.cos(a) * r, 116 - 2 * (k / 15) + Math.sin(a) * r * 0.9]); }
      const p = document.createElementNS(NS, 'path'); p.setAttribute('d', 'M' + pts.map((q) => q[0].toFixed(1) + ' ' + q[1].toFixed(1)).join('L') + 'Z');
      p.setAttribute('pathLength', '1'); p.setAttribute('fill', 'none'); p.setAttribute('stroke', '#C29A62'); p.setAttribute('stroke-opacity', String(0.42 - k * 0.01)); p.setAttribute('stroke-width', '1'); p.setAttribute('vector-effect', 'non-scaling-stroke');
      p.style.strokeDasharray = '1'; p.style.strokeDashoffset = still ? '0' : '1'; svg.append(p); paths.push(p);
    }
    slot.append(svg);
    if (!still && window.gsap) window.ScrollTrigger.create({ trigger: slot, start: 'top 82%', end: 'bottom 35%', scrub: 1, animation: window.gsap.to(paths, { strokeDashoffset: 0, ease: 'none', stagger: { each: 0.06 } }) });
  }

  BFF.fx.progress = {
    init(opts) {
      const still = !!(opts && opts.still);
      const gg = gauge();
      if (gg) {
        const tick = () => { const y = window.scrollY + innerHeight / 2; gg.dot.style.transform = `translateY(${(depthAt(y) * 64).toFixed(1)}px)`; };
        tick(); window.addEventListener('scroll', tick, { passive: true });
      }
      rings(still);
    }
  };
})();
