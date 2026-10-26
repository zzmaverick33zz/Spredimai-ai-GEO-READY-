/* Effect 3: "The lift". The pinned chapter III becomes a layered zoom with depth.
   Behaviour modelled on 21st.dev "Zoom Parallax" (efferd; framer-motion useScroll/useTransform, scale ranges per layer) and
   "Depth Parallax Scene" (rmahammad, MIT; layers travel at depth-proportional rates and drift with the pointer).
   Sources need an API key and could not be read; this is written from their documented behaviour, on GSAP ScrollTrigger scrub.
   Layers, far to near: the S05 media (zooms 1 -> 1.35), a warm daylight glow (screen blend), spray droplets (zoom 1 -> 1.9).
   The ground still goes --deep -> --peat, so the next chapter keeps the dark -> light order; the daylight is a glow that
   peaks during the lift and recedes. The headline arrives late in the pin. */
(function () {
  'use strict';
  const { $, gsap, reduce } = Object.assign({}, BFF, { gsap: window.gsap });

  function el(tag, cls) { const e = document.createElement(tag); e.className = cls; e.setAttribute('aria-hidden', 'true'); return e; }

  BFF.fx.lift = {
    init({ pin } = { pin: true }) {
      const sec = $('#ch3'); if (!sec) return;
      const slot = $('.slot', sec), body = $('.interlude__body', sec);
      const sky = el('div', 'lift__sky'), spray = el('div', 'lift__spray');
      const nd = BFF.coarse ? 14 : 24;
      for (let i = 0; i < nd; i++) {                                                     // a fixed pseudo-random scatter, no layout cost
        const d = document.createElement('i'), k = (i * 37 % 100) / 100, s = 2 + (i * 53 % 5);
        d.style.cssText = `left:${(i * 61 % 100)}%;top:${(i * 29 % 100)}%;width:${s}px;height:${s * 1.35}px;opacity:${(0.25 + k * 0.5).toFixed(2)}`;
        spray.append(d);
      }
      slot.after(sky); sky.after(spray);

      const tl = gsap.timeline({ scrollTrigger: {
        trigger: sec, start: pin ? 'top top' : 'top bottom', end: pin ? '+=150%' : 'bottom top',
        pin, scrub: 1, anticipatePin: 1
      } });
      tl.fromTo(slot, { scale: 1, yPercent: 8, transformOrigin: '60% 70%' }, { scale: 1.35, yPercent: -3, ease: 'none', duration: 1.1 }, 0)
        .fromTo(sky, { opacity: 0, scale: 1 }, { opacity: 0.9, scale: 1.12, ease: 'none', duration: 0.6 }, 0.1)
        .to(sky, { opacity: 0.1, ease: 'none', duration: 0.4 }, 0.7)
        .fromTo(spray, { scale: 1, yPercent: 0, autoAlpha: 1 }, { scale: 1.9, yPercent: 22, ease: 'none', duration: 1.1 }, 0)
        .to(spray, { autoAlpha: 0, ease: 'none', duration: 0.35 }, 0.7)
        .fromTo(sec, { backgroundColor: BFF.css('--deep') }, { backgroundColor: BFF.css('--peat'), ease: 'none', duration: 1.1 }, 0)
        .fromTo(Array.from(body.children), { y: 40, autoAlpha: 0 }, { y: 0, autoAlpha: 1, stagger: 0.12, ease: 'power2.out', duration: 0.3 }, 0.66);

      // pointer drift: nearest layer +-8 px, the media +-3 px (mouse only)
      if (!BFF.coarse) {
        const sx = gsap.quickTo(spray, 'x', { duration: 0.9, ease: 'power3.out' }), sy = gsap.quickTo(spray, 'y', { duration: 0.9, ease: 'power3.out' });
        const mx = gsap.quickTo(slot, 'x', { duration: 1.2, ease: 'power3.out' });
        sec.addEventListener('pointermove', (e) => {
          const r = sec.getBoundingClientRect(), nx = (e.clientX - r.left) / r.width - 0.5, ny = (e.clientY - r.top) / r.height - 0.5;
          sx(-nx * 16); sy(-ny * 16); mx(nx * 6);
        }, { passive: true });
      }
    }
  };
})();
