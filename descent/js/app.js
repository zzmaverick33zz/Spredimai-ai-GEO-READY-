/* Big Foot Floors: page logic (restored from the v1 build). Effects live in js/effects/*.js and plug in via BFF.fx. */
(function () {
  'use strict';
  const { $, $$ } = BFF;
  const { gsap, ScrollTrigger } = window;
  document.documentElement.classList.add('js');
  gsap.registerPlugin(ScrollTrigger);
  const reduce = BFF.reduce, isStatic = BFF.isStatic;

  /* ---------- media brief toggle (#clean hides briefs) ---------- */
  const toggle = $('#briefToggle');
  const setBrief = (on) => {
    document.body.classList.toggle('show-brief', on);
    toggle.setAttribute('aria-pressed', String(on));
    $('span', toggle).textContent = on ? 'Media brief: on' : 'Media brief: off';
  };
  setBrief(location.hash !== '#clean');
  toggle.addEventListener('click', () => setBrief(!document.body.classList.contains('show-brief')));
  window.addEventListener('hashchange', () => { if (location.hash === '#clean') setBrief(false); });

  /* ---------- header, drawer ---------- */
  const hdr = $('#hdr');
  const onScroll = () => hdr.classList.toggle('is-solid', window.scrollY > 40);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  const btn = $('#menuBtn'), drawer = $('#drawer');
  const setMenu = (open) => {
    drawer.hidden = !open;
    btn.setAttribute('aria-expanded', String(open));
    btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.documentElement.style.overflow = open ? 'hidden' : '';
  };
  btn.addEventListener('click', () => setMenu(drawer.hidden));
  drawer.addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !drawer.hidden) { setMenu(false); btn.focus(); } });

  /* ---------- projects reel ---------- */
  const reel = $('#reel');
  $$('.reel-nav button').forEach((b) => b.addEventListener('click', () => {
    reel.scrollBy({ left: Number(b.dataset.dir) * reel.clientWidth * 0.8, behavior: reduce ? 'auto' : 'smooth' });
  }));

  /* ---------- video: pause off-screen, poster only on reduced motion ---------- */
  const vio = new IntersectionObserver((es) => es.forEach((e) => {
    const v = e.target; e.isIntersecting ? v.play && v.play().catch(() => {}) : v.pause && v.pause();
  }), { threshold: 0.15 });
  $$('.slot video').forEach((v) => { if (reduce) { v.removeAttribute('autoplay'); v.pause(); } else vio.observe(v); });

  /* ---------- smooth scroll ---------- */
  let lenis = null;
  if (!reduce) {
    lenis = new window.Lenis({ lerp: 0.09, wheelMultiplier: 0.9 });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((t) => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
  }
  BFF.lenis = lenis;
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href^="#"]');
    if (!a || a.getAttribute('href') === '#') return;
    const t = $(a.getAttribute('href'));
    if (!t) return;
    e.preventDefault();
    if (lenis) lenis.scrollTo(t, { offset: -70, duration: 1.4 }); else t.scrollIntoView({ behavior: 'auto' });
    history.replaceState(null, '', a.getAttribute('href') === '#top' ? location.pathname + location.search : a.getAttribute('href'));
    t.setAttribute('tabindex', '-1'); t.focus({ preventScroll: true });
  });

  /* ---------- rail: active chapter + progress line (works without motion) ---------- */
  const rail = $('#rail'), links = $$('a', rail), targets = links.map((a) => $(a.getAttribute('href')));
  const first = targets[0], last = $('#arrival');
  const rio = new IntersectionObserver((entries) => entries.forEach((en) => {
    if (en.isIntersecting) {
      const i = targets.indexOf(en.target);
      links.forEach((l, j) => { l.classList.toggle('is-active', i === j); if (i === j) l.setAttribute('aria-current', 'true'); else l.removeAttribute('aria-current'); });
    }
  }), { rootMargin: '-45% 0px -50% 0px' });
  targets.forEach((t) => rio.observe(t));
  const bar = $('.rail__bar > i', rail);
  const railVis = () => {
    const y = window.scrollY + innerHeight / 2, top = (el) => el.getBoundingClientRect().top + window.scrollY;
    const a = top(first), b = top(last);
    rail.classList.toggle('is-on', y > a && y < b + innerHeight * 0.4);
    bar.style.transform = `scaleY(${Math.min(1, Math.max(0, (y - a) / (b - a)))})`;
  };
  railVis();
  window.addEventListener('scroll', railVis, { passive: true });

  /* ---------- motion ---------- */
  const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  BFF.css = css;

  function splitWords(el) {
    const walk = (node) => {
      Array.from(node.childNodes).forEach((n) => {
        if (n.nodeType === 3) {
          const frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach((w) => {
            if (!w) return;
            if (/^\s+$/.test(w)) { frag.append(' '); return; }
            const m = document.createElement('span'); m.className = 'line-mask';
            const s = document.createElement('span'); s.textContent = w; m.append(s); frag.append(m);
          });
          n.replaceWith(frag);
        } else if (n.nodeType === 1) walk(n);
      });
    };
    walk(el);
    return $$('.line-mask > span', el);
  }

  function heroIntro() {
    const words = splitWords($('#h-hero'));
    gsap.timeline({ defaults: { ease: 'power3.out' } })
      .set('.hero__veil', { opacity: 1 })
      .to('.hero__veil', { opacity: 0, duration: 1.8, ease: 'power2.out' }, 0)
      .from(words, { yPercent: 110, duration: 0.9, stagger: 0.07 }, 0.35)
      .fromTo('.hero .slot img, .hero .slot canvas', { scale: 1.12 }, { scale: 1, duration: 7, ease: 'power2.out' }, 0)
      .from('.hero__ctas, .hero__facts', { autoAlpha: 0, y: 14, duration: 0.7, stagger: 0.12 }, 0.9);
  }

  function colourByDepth() {
    const colours = { silt: css('--silt'), deep: css('--deep'), peat: css('--peat'), char: css('--char'), oak: css('--oak'), linen: css('--linen') };
    const set = (c) => gsap.to(document.body, { backgroundColor: c, duration: 0.9, ease: 'power2.out', overwrite: 'auto' });
    [...$$('.chapter').map((el) => [el, colours[el.dataset.g]]), [$('#ch3'), colours.peat]].forEach(([el, c]) => ScrollTrigger.create({
      trigger: el, start: 'top 60%', end: 'bottom 60%', onToggle: (s) => s.isActive && set(c)
    }));
  }

  // v1 behaviour: the one pinned moment. Replaced by BFF.fx.lift when that effect is present.
  function liftV1() {
    const sec = $('#ch3'), slot = $('.slot', sec);
    gsap.timeline({ scrollTrigger: { trigger: sec, start: 'top top', end: '+=100%', pin: true, scrub: 1, anticipatePin: 1 } })
      .fromTo(slot, { yPercent: 16, scale: 1.14 }, { yPercent: 0, scale: 1, ease: 'none' }, 0)
      .fromTo(sec, { backgroundColor: css('--deep') }, { backgroundColor: css('--peat'), ease: 'none' }, 0)
      .fromTo($$('.interlude__body > *', sec), { y: 40, autoAlpha: 0 }, { y: 0, autoAlpha: 1, stagger: 0.15, ease: 'power2.out' }, 0.35);
  }

  function parallax() {
    $$('.chapter__media').forEach((m) => {
      const main = $('.slot--main, .slot--wide', m), detail = $('.slot--detail', m);
      const run = (el, from, to) => el && gsap.fromTo(el, { yPercent: from }, { yPercent: to, ease: 'none', scrollTrigger: { trigger: m, start: 'top bottom', end: 'bottom top', scrub: true } });
      run(main, 5, -5);
      run(detail, 12, -4);   // detail drifts later than the main frame
    });
    $$('.arrival .slot, .heritage .slot').forEach((s) => gsap.fromTo(s, { yPercent: 6 }, { yPercent: -6, ease: 'none', scrollTrigger: { trigger: s, start: 'top bottom', end: 'bottom top', scrub: true } }));
  }

  function reveals() {
    $$('.chapter__text, .arrival__head, .sec-head').forEach((el) => gsap.from(el.children, {
      opacity: 0, y: 24, duration: 0.8, ease: 'power3.out', stagger: 0.1, scrollTrigger: { trigger: el, start: 'top 82%', once: true }   // opacity only: autoAlpha sets visibility:hidden, which made the slider unreachable by keyboard
    }));
  }

  /* effects that need no scroll timeline start here (ripple, torch, compare ...) */
  const startFx = (name, ...args) => { const f = BFF.fx[name]; if (f && f.init) { try { f.init(...args); } catch (err) { console.warn('[fx:' + name + ']', err); } } };

  const mm = gsap.matchMedia();
  mm.add(isStatic ? '(max-width: 0px)' : '(prefers-reduced-motion: no-preference)', () => {
    heroIntro();
    if (innerWidth >= 900) { if (BFF.fx.lift) startFx('lift', { pin: true }); else liftV1(); }   // pin first: later triggers measure after its spacer
    else if (BFF.fx.lift) startFx('lift', { pin: false });
    colourByDepth();
    reveals();
    parallax();
    ['ripple', 'torch', 'counter', 'progress'].forEach((n) => startFx(n));
  });
  // reduced motion: nothing moves; chapters keep their own grounds. Interactive widgets still work.
  mm.add(isStatic ? '(min-width: 0px)' : '(prefers-reduced-motion: reduce)', () => {
    document.documentElement.classList.remove('js');
    ['counter', 'progress'].forEach((n) => startFx(n, { still: true }));
  });
  startFx('compare');   // interactive, works with and without motion

  /* ---------- consultation form ---------- */
  (function form() {
    const ENDPOINT = window.BFF_FORM_ENDPOINT || '';
    const f = $('#form'), done = $('#formDone'), note = $('#stubNote');
    if (ENDPOINT && note) note.remove();
    const err = document.createElement('p'); err.className = 'form-error'; err.setAttribute('role', 'alert'); err.hidden = true;
    f.querySelector('button[type=submit]').parentElement.append(err);
    f.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = f.elements.email, name = f.elements.name;
      const okEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim());
      email.closest('.field').classList.toggle('is-invalid', !okEmail);
      $('#f-email-err').hidden = okEmail;
      name.closest('.field').classList.toggle('is-invalid', !name.value.trim());
      if (!name.value.trim()) { name.focus(); return; }
      if (!okEmail) { email.focus(); return; }
      const fd = new FormData(f), payload = Object.assign({}, Object.fromEntries(fd), { type: fd.getAll('type') });
      const submit = f.querySelector('button[type=submit]'); submit.disabled = true; err.hidden = true;
      try {
        if (ENDPOINT) { const r = await fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }); if (!r.ok) throw new Error(String(r.status)); }
        else await new Promise((r) => setTimeout(r, 400));
        f.hidden = true; done.hidden = false; done.setAttribute('tabindex', '-1'); done.focus();
      } catch (_) { err.textContent = 'Something went wrong. Please try again or write to info@bffloors.com.'; err.hidden = false; submit.disabled = false; }
    });
  })();

  window.addEventListener('load', () => ScrollTrigger.refresh());
})();
