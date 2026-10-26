/* Cursor system. A precise brass dot, a springy ring, and a label pill that says what a click will do.
   Pattern after 21st.dev "Intent Label" (MIT: a custom cursor that morphs from a dot into a labelled pill when hovering elements
   marked with data-intent, with spring motion and drag feedback) and "Fluid Magnetic Cursor" (spring / magnetic feel).
   The component sources need an API key and could not be read, so this is written from their documented behaviour.
   Markup: data-cursor="View|Drag|Scroll|..." on any element. Buttons and links get a soft magnetic pull.
   Mouse only (fine pointer, hover capable). Reduced motion: no springs, no magnet, the ring snaps. Forms keep the native cursor.
   Only transform / opacity are animated. */
(function () {
  'use strict';
  const { $$ } = BFF;
  BFF.fx.cursor = {
    init() {
      if (BFF.coarse) return;
      const root = document.createElement('div'); root.className = 'cur'; root.setAttribute('aria-hidden', 'true');
      root.innerHTML = '<i class="cur__ring"></i><i class="cur__dot"></i><span class="cur__label"></span>';
      document.body.append(root);
      const ring = root.querySelector('.cur__ring'), dot = root.querySelector('.cur__dot'), label = root.querySelector('.cur__label');
      const still = BFF.reduce;
      let x = -200, y = -200, rx = x, ry = y, vx = 0, vy = 0, raf = 0, shown = false, down = false, text = '';
      // spring for the ring (stiffness / damping tuned for a soft but quick follow); the dot is exact
      const K = 0.16, D = 0.72;
      const loop = () => {
        if (still) { rx = x; ry = y; vx = vy = 0; }
        else { vx = (vx + (x - rx) * K) * D; vy = (vy + (y - ry) * K) * D; rx += vx; ry += vy; }
        dot.style.transform = 'translate3d(' + x + 'px,' + y + 'px,0)';
        ring.style.transform = 'translate3d(' + rx.toFixed(2) + 'px,' + ry.toFixed(2) + 'px,0)';
        label.style.transform = 'translate3d(' + rx.toFixed(2) + 'px,' + ry.toFixed(2) + 'px,0)';
        raf = (Math.abs(x - rx) + Math.abs(y - ry) + Math.abs(vx) + Math.abs(vy) > 0.05) ? requestAnimationFrame(loop) : 0;
      };
      const kick = () => { if (!raf) raf = requestAnimationFrame(loop); };
      const setState = (el) => {
        const lbl = el && el.closest('[data-cursor]'), link = el && el.closest('a,button,[role=button],[role=slider],summary,label,.chips label');
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
        setState(e.target); kick();
      }, { passive: true });
      document.addEventListener('pointerdown', () => { down = true; root.classList.add('is-down'); });
      addEventListener('pointerup', () => { down = false; root.classList.remove('is-down'); });
      document.documentElement.addEventListener('pointerleave', () => { shown = false; root.classList.remove('is-on'); document.documentElement.classList.remove('has-cursor'); });
      document.documentElement.addEventListener('pointerenter', () => { root.classList.add('is-on'); });

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
