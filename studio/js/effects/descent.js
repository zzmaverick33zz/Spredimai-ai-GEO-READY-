/* "The descent": seven short films play at their natural speed. Scroll does not scrub video; it only moves from one scene
   to the next, and each change is a timed cross-dissolve (opacity + a slow push-in), so playback is always smooth and sharp.
   Only the current and the next scene are loaded / playing. Captions rise word by word (CSS transitions, transform only).
   Each scene is a seamless loop (see process_scenes.py). Fallbacks: reduced motion / ?static -> first scene poster + caption, no pin. A video that fails keeps its poster. */
(function () {
  'use strict';
  const { $, $$, clamp } = BFF;
  BFF.fx.film = {
    init() {
      const sec = $('#film'); if (!sec) return;
      const gsap = window.gsap, ST = window.ScrollTrigger;
      const scenes = $$('.scene', sec), caps = $$('.dcap', sec), dots = $$('.ddot', sec), N = scenes.length;
      const vids = scenes.map((s) => $('video', s)), depth = scenes.map((s) => parseFloat(s.dataset.depth));
      const gdot = $('.descent__gauge b', sec), bar = $('.descent__bar i', sec), hint = $('.descent__hint', sec), stage = $('.descent__stage', sec);
      const loaded = new Set();
      const load = (i) => { if (i < 0 || i >= N || loaded.has(i)) return; loaded.add(i); vids[i].preload = 'auto'; vids[i].load(); };
      let cur = 0, st = null;
      const go = (i) => {
        if (i === cur) return;
        const prev = cur; cur = i;
        scenes.forEach((s, k) => { s.classList.toggle('is-on', k === i); s.classList.toggle('is-prev', k === prev); });
        caps.forEach((c, k) => c.classList.toggle('is-on', k === i));
        dots.forEach((d, k) => { d.classList.toggle('is-on', k === i); if (k === i) d.setAttribute('aria-current', 'true'); else d.removeAttribute('aria-current'); });
        const v = vids[i]; load(i); try { v.currentTime = 0; } catch (_) {} const p = v.play(); if (p && p.catch) p.catch(() => {});
        load(i + 1);
        clearTimeout(go.t); go.t = setTimeout(() => { vids.forEach((x, k) => { if (k !== cur) { x.pause(); scenes[k].classList.remove('is-prev'); } }); }, 1500);
        gsap.to(gdot, { y: depth[i] * 91, duration: 1.6, ease: 'power2.inOut', overwrite: 'auto' });
      };
      const start = () => {
        st = ST.create({
          trigger: sec, start: 'top top', end: () => '+=' + Math.round(innerHeight * N * (innerWidth < 760 ? 0.4 : 0.46)), pin: true, anticipatePin: 1,
          onUpdate: (self) => {
            go(clamp(Math.floor(self.progress * N), 0, N - 1));
            bar.style.transform = 'scaleX(' + self.progress.toFixed(4) + ')';
            hint.style.opacity = self.progress > 0.02 ? 0 : 1;
          }
        });
        dots.forEach((d, i) => d.addEventListener('click', () => {
          const y = st.start + (i + 0.5) / N * (st.end - st.start);
          if (BFF.lenis) BFF.lenis.scrollTo(y, { duration: 1.6 }); else window.scrollTo(0, y);
        }));
        // pointer parallax: the whole picture drifts a few pixels against the pointer (mouse only)
        if (!BFF.coarse) {
          const qx = gsap.quickTo(stage, '--px', { duration: 1.2, ease: 'power3.out' }), qy = gsap.quickTo(stage, '--py', { duration: 1.2, ease: 'power3.out' });
          stage.addEventListener('pointermove', (e) => { qx((e.clientX / innerWidth - 0.5) * -22); qy((e.clientY / innerHeight - 0.5) * -14); });
        }
      };
      // scene 1 plays as soon as the page has settled; scene 2 is fetched right after, so the first change is instant
      const boot = () => { load(0); load(1); const p = vids[0].play(); if (p && p.catch) p.catch(() => {}); };
      new IntersectionObserver((es, o) => { if (es.some((e) => e.isIntersecting)) { boot(); o.disconnect(); } }, { rootMargin: '100% 0px' }).observe(sec);
      new IntersectionObserver((es) => es.forEach((e) => { const v = vids[cur]; if (e.isIntersecting) { const p = v.play(); if (p && p.catch) p.catch(() => {}); } else vids.forEach((x) => x.pause()); }), { threshold: 0.05 }).observe(stage);
      start();
    }
  };
})();
