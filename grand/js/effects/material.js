/* "The material": colour tones, two stat rings, trunk diagram, growth rings.
   Reference for the idea: the bogoak.fr "bogwood logs" infographic (age tones, brass-outlined stat circles, dimensioned log, cross-section).
   All drawing is original SVG. Numbers: Big Foot Floors has not supplied them, so every figure is a marked placeholder ("—").
   Open the page with #example to preview how filled-in values look; those preview numbers come from the public reference and are labelled as not Big Foot data.
   Draw-in animations use stroke-dashoffset once on entry; everything else is transform / opacity. */
(function () {
  'use strict';
  const { $, $$ } = BFF;
  BFF.fx.material = {
    init(opts) {
      const sec = $('#material'); if (!sec) return;
      if (location.hash === '#example') {
        $$('[data-ph]', sec).forEach((b) => { if (b.dataset.ex) { b.textContent = b.dataset.ex; b.removeAttribute('data-ph'); b.classList.add('is-example'); } });
        sec.classList.add('is-example'); const n = $('[data-example]', sec); if (n) n.hidden = false;
        const t = $('[data-example-note]', sec); if (t) t.hidden = true;
      }
      if (opts && opts.still) return;
      const gsap = window.gsap;
      const once = (el, vars, start = 'top 80%') => window.ScrollTrigger.create({ trigger: el, start, once: true, onEnter: vars });
      // tones rise one by one, the line draws underneath
      once($('.tones', sec), () => {
        gsap.from($$('.tone', sec), { opacity: 0, y: 48, duration: 1.1, ease: 'power3.out', stagger: 0.16 });
        gsap.fromTo($('.tones__line b', sec), { scaleX: 0 }, { scaleX: 1, duration: 1.8, ease: 'power2.inOut', delay: 0.2 });
      });
      // stat rings draw themselves
      $$('.stat', sec).forEach((s) => once(s, () => {
        const ring = $('.stat__ring', s);
        gsap.fromTo(ring, { strokeDashoffset: 1 }, { strokeDashoffset: parseFloat(s.dataset.off), duration: 2.2, ease: 'power3.out' });
        gsap.from($('div', s), { opacity: 0, scale: 0.9, duration: 1.2, ease: 'power3.out', delay: 0.3 });
      }));
      // dated samples: each bar grows from today towards its age
      once($('.dates', sec), () => {
        $$('.dates li', sec).forEach((li, i) => {
          gsap.fromTo([$('.dates__err', li), $('.dates__dot', li)], { scaleX: 0 }, { scaleX: 1, duration: 1.6, ease: 'power3.out', delay: 0.15 * i });
          gsap.from([$('.dates__n', li), $('.dates__v', li)], { opacity: 0, y: 12, duration: 0.9, ease: 'power3.out', delay: 0.15 * i });
        });
      }, 'top 85%');
      // log outline, then dimension lines
      const lg = $('.logsvg', sec);
      once(lg, () => {
        gsap.fromTo($('.log', lg), { strokeDasharray: 2200, strokeDashoffset: 2200 }, { strokeDashoffset: 0, duration: 2, ease: 'power2.inOut' });
        gsap.from($('.grainl', lg), { opacity: 0, duration: 1.2, delay: 1.2 });
        gsap.from($('.dim', lg), { opacity: 0, duration: 1, delay: 1.6 });
      });
      // growth rings: from the pith outwards, in the order a tree grew them
      const rg = $('.rings', sec), paths = $$('path:not(.crack)', rg);
      gsap.set(paths, { strokeDasharray: 1, strokeDashoffset: 1 });
      once(rg, () => {
        gsap.to(paths, { strokeDashoffset: 0, duration: 1.4, ease: 'power2.out', stagger: 0.12 });
        gsap.fromTo($('.crack', rg), { strokeDasharray: 1, strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 1.2, delay: 1.8, ease: 'power1.out' });
      }, 'top 75%');
    }
  };
})();
