/* Cursor: a tree's growth rings. A brass core follows the pointer exactly; around it irregular rings, hand-drawn like the
   cross-section of a trunk, follow with a soft spring and slowly turn. Hold still and the tree grows another ring (up to six);
   move fast and the rings draw back in. Over a link the core swells, over an element marked data-cursor="..." a brass
   tag says what a click or drag does. A press sends one ring outwards.
   Mouse only (fine pointer + hover). Reduced motion: rings are static and snap to the pointer. Form fields keep the native cursor.
   Only transform / opacity are animated. */
(function () {
  'use strict';
  const { $$ } = BFF;
  const NS = 'http://www.w3.org/2000/svg', RINGS = 6;
  // one irregular closed curve per ring, deterministic so every visit looks the same
  const ringPath = (k) => {
    const r0 = 9 + k * 6.2, pts = [], n = 36;
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2, w = 1 + 0.07 * Math.sin(3 * a + k * 1.7) + 0.045 * Math.sin(5 * a + k * 2.9) + 0.025 * Math.sin(8 * a + k * 0.6);
      pts.push([Math.cos(a) * r0 * w, Math.sin(a) * r0 * w]);
    }
    let d = 'M' + pts[0].map((v) => v.toFixed(2)).join(',');
    for (let i = 0; i < n; i++) {                                                // smooth closed curve through the points (Catmull-Rom to Bezier)
      const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n];
      const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6], c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
      d += 'C' + c1.map((v) => v.toFixed(2)).join(',') + ' ' + c2.map((v) => v.toFixed(2)).join(',') + ' ' + p2.map((v) => v.toFixed(2)).join(',');
    }
    return d + 'Z';
  };
  BFF.fx.cursor = {
    init() {
      if (BFF.coarse) return;
      const still = BFF.reduce;
      const root = document.createElement('div'); root.className = 'cur'; root.setAttribute('aria-hidden', 'true');
      const svg = document.createElementNS(NS, 'svg'); svg.setAttribute('class', 'cur__rings'); svg.setAttribute('viewBox', '-50 -50 100 100');
      const paths = [];
      for (let k = 0; k < RINGS; k++) { const p = document.createElementNS(NS, 'path'); p.setAttribute('d', ringPath(k)); svg.append(p); paths.push(p); }
      const core = document.createElement('i'); core.className = 'cur__core';
      const label = document.createElement('span'); label.className = 'cur__label';
      root.append(svg, core, label); document.body.append(root);

      let x = -200, y = -200, rx = x, ry = y, vx = 0, vy = 0, shown = false, text = '', grow = still ? 3 : 1, spin = 0, last = performance.now(), shownRings = -1, speed = 0, pulse = 0, hold = 0;
      const K = 0.14, D = 0.74;
      const paint = () => {
        const n = Math.round(grow * 10) / 10, vis = Math.min(RINGS, Math.floor(n));
        if (vis !== shownRings) { shownRings = vis; paths.forEach((p, k) => { p.style.opacity = k < vis ? String(0.9 - k * 0.11) : '0'; }); }
      };
      const loop = (now) => {
        const dt = Math.min(48, now - last); last = now;
        if (still) { rx = x; ry = y; }
        else {
          vx = (vx + (x - rx) * K) * D; vy = (vy + (y - ry) * K) * D; rx += vx; ry += vy;
          speed += (Math.hypot(vx, vy) - speed) * 0.2;
          if (speed < 0.6) grow = Math.min(RINGS, grow + dt / 1100);               // dwelling: grow a ring about every 1.1 s
          else if (speed > 3) grow = Math.max(1, grow - dt / 220);                  // moving: draw back to a single ring
          spin += dt * 0.012;
        }
        const s = 1 + (hold ? 0.35 : 0) + (root.classList.contains('is-link') ? 0.25 : 0);
        svg.style.transform = 'translate3d(' + rx.toFixed(2) + 'px,' + ry.toFixed(2) + 'px,0) rotate(' + spin.toFixed(1) + 'deg) scale(' + s.toFixed(2) + ')';
        core.style.translate = x + 'px ' + y + 'px';
        label.style.translate = rx.toFixed(2) + 'px ' + ry.toFixed(2) + 'px';
        paint();
        requestAnimationFrame(loop);
      };
      const setState = (el) => {
        const lbl = el && el.closest('[data-cursor]'), link = el && el.closest('a,button,[role=button],[role=slider],summary,label');
        const field = el && el.closest('input,textarea,select');
        root.classList.toggle('is-field', !!field);
        const t = lbl ? lbl.dataset.cursor : '';
        if (t !== text) { text = t; label.textContent = t; }
        root.classList.toggle('has-label', !!t && !field);
        root.classList.toggle('is-link', !!link && !t && !field);
        root.classList.toggle('on-light', !!(el && el.closest('.light')));
      };
      addEventListener('pointermove', (e) => {
        if (e.pointerType !== 'mouse') return;
        x = e.clientX; y = e.clientY;
        if (!shown) { shown = true; rx = x; ry = y; root.classList.add('is-on'); document.documentElement.classList.add('has-cursor'); }
        setState(e.target);
      }, { passive: true });
      document.addEventListener('pointerdown', (e) => {
        if (e.pointerType !== 'mouse') return;
        hold = 1;
        const p = document.createElement('i'); p.className = 'cur__pulse'; p.style.translate = x + 'px ' + y + 'px';
        root.append(p); p.addEventListener('animationend', () => p.remove());
      });
      addEventListener('pointerup', () => { hold = 0; });
      document.documentElement.addEventListener('pointerleave', () => { shown = false; root.classList.remove('is-on'); document.documentElement.classList.remove('has-cursor'); });
      document.documentElement.addEventListener('pointerenter', () => { root.classList.add('is-on'); });
      requestAnimationFrame(loop);

      // magnetic pull on buttons: the element leans toward the pointer inside a small halo
      if (!still && window.gsap) {
        $$('.btn, .hdr__cta, .menu-btn, .reel-nav button').forEach((b) => {
          const qx = window.gsap.quickTo(b, 'x', { duration: 0.5, ease: 'power3.out' }), qy = window.gsap.quickTo(b, 'y', { duration: 0.5, ease: 'power3.out' });
          b.addEventListener('pointermove', (e) => { if (e.pointerType !== 'mouse') return; const r = b.getBoundingClientRect(); qx((e.clientX - (r.left + r.width / 2)) * 0.22); qy((e.clientY - (r.top + r.height / 2)) * 0.28); });
          b.addEventListener('pointerleave', () => { qx(0); qy(0); });
        });
      }
    }
  };
})();
