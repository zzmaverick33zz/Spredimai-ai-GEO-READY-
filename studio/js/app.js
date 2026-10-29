/* Big Foot Floors, studio build: page logic. Effects live in js/effects/*.js, the specification tool in js/studio.js. */
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
  setBrief(location.hash === '#brief');
  if (location.hash === '#brief') toggle.hidden = false;   // team-only: add #brief to the URL to see the media briefs
  toggle.addEventListener('click', () => setBrief(!document.body.classList.contains('show-brief')));
  window.addEventListener('hashchange', () => { setBrief(location.hash === '#brief'); toggle.hidden = location.hash !== '#brief'; });

  /* ---------- header, drawer ---------- */
  const hdr = $('#hdr');
  const topBar = document.createElement('div'); topBar.className = 'topbar'; topBar.setAttribute('aria-hidden', 'true'); topBar.innerHTML = '<i></i>'; document.body.prepend(topBar);
  let lastY = window.scrollY, hidden = false;
  const onScroll = () => {
    const y = window.scrollY, dy = y - lastY;
    hdr.classList.toggle('is-solid', y > 40);
    if (Math.abs(dy) > 6) {                                       // hide while diving down, return on any move up (never while the menu is open)
      const hide = dy > 0 && y > 320 && drawer.hidden;
      if (hide !== hidden) { hidden = hide; hdr.classList.toggle('is-away', hide); }
      lastY = y;
    }
    topBar.firstChild.style.transform = 'scaleX(' + Math.min(1, y / Math.max(1, document.documentElement.scrollHeight - innerHeight)).toFixed(4) + ')';
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  hdr.addEventListener('focusin', () => { hidden = false; hdr.classList.remove('is-away'); });

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

  // drag the projects reel with the mouse (touch already scrolls natively)
  (function () {
    let down = false, sx = 0, sl = 0, moved = false;
    reel.addEventListener('pointerdown', (e) => { if (e.pointerType !== 'mouse') return; down = true; moved = false; sx = e.clientX; sl = reel.scrollLeft; reel.style.scrollSnapType = 'none'; reel.classList.add('is-drag'); });
    window.addEventListener('pointermove', (e) => { if (!down) return; const dx = e.clientX - sx; if (Math.abs(dx) > 4) moved = true; reel.scrollLeft = sl - dx; });
    window.addEventListener('pointerup', () => { if (!down) return; down = false; reel.classList.remove('is-drag'); reel.style.scrollSnapType = ''; });
    reel.addEventListener('click', (e) => { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
  })();

  /* ---------- video: pause off-screen, poster only on reduced motion ---------- */
  const vio = new IntersectionObserver((es) => es.forEach((e) => {
    const v = e.target; e.isIntersecting ? v.play && v.play().catch(() => {}) : v.pause && v.pause();
  }), { threshold: 0.15 });
  // videos start AFTER the page has painted and settled (their decode would otherwise compete with the first paint)
  const armVideos = () => $$('.slot video').forEach((v) => { if (reduce) { v.removeAttribute('autoplay'); v.pause(); } else vio.observe(v); });
  if (document.readyState === 'complete') setTimeout(armVideos, 300); else window.addEventListener('load', () => setTimeout(armVideos, 300), { once: true });
  // buffer a video before it scrolls in (preload=none keeps the first paint light; this avoids a hitch when it arrives)
  const near = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.preload = 'auto'; near.unobserve(e.target); } }), { rootMargin: '90% 0px' });
  $$('.slot video').forEach((v) => { if (!reduce) near.observe(v); });

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
    gsap.timeline({ defaults: { ease: 'power3.out' }, delay: BFF.introDelay || 0 })
      .set('.hero__veil', { opacity: 1 })
      .to('.hero__veil', { opacity: 0, duration: 1.8, ease: 'power2.out' }, 0)
      .from(words, { yPercent: 110, duration: 0.9, stagger: 0.07 }, 0.35)
      .fromTo('.hero .slot img, .hero .slot video', { scale: 1.12 }, { scale: 1, duration: 7, ease: 'power2.out' }, 0)
      .from('.hero__ctas, .hero__facts', { autoAlpha: 0, y: 14, duration: 0.7, stagger: 0.12 }, 0.9);
  }

  // headings rise out of a mask, word by word (transform only)
  function headings() {
    $$('.sh h2, .heritage h2, .consult h2').forEach((h) => {
      ScrollTrigger.create({ trigger: h, start: 'top 94%', once: true, onEnter: () => gsap.from(splitWords(h), { yPercent: 118, duration: 1, ease: 'power3.out', stagger: 0.055 }) });
    });
  }
  function reveals() {
    $$('.sh > *:not(h2), .tl li, .pr li, .env__card, .spc li, .mk__item, .spec__card, .hot, .col .hot__list').forEach((el) => gsap.from(el, { opacity: 0, y: 28, duration: 0.9, ease: 'power3.out', scrollTrigger: { trigger: el, start: 'top 90%', once: true } }));   // opacity only: autoAlpha would make controls unreachable by keyboard
  }
  function parallax() {
    $$('.env__card figure img, .heritage .slot').forEach((s) => gsap.fromTo(s, { yPercent: -5 }, { yPercent: 5, ease: 'none', scrollTrigger: { trigger: s.parentElement, start: 'top bottom', end: 'bottom top', scrub: true } }));
  }
  const startFx = (name, ...args) => { const f = BFF.fx[name]; if (f && f.init) { try { f.init(...args); } catch (err) { console.warn('[fx:' + name + ']', err); } } };

  const mm = gsap.matchMedia();
  mm.add(isStatic ? '(max-width: 0px)' : '(prefers-reduced-motion: no-preference)', () => {
    heroIntro();
    reveals(); headings(); parallax();
    startFx('material');
  });
  mm.add(isStatic ? '(min-width: 0px)' : '(prefers-reduced-motion: reduce)', () => {
    document.documentElement.classList.remove('js');
    startFx('material', { still: true });
  });
  startFx('studio');
  startFx('journey');
  startFx('cursor');

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
      const fd = new FormData(f), payload = Object.assign({}, Object.fromEntries(fd), { species: fd.getAll('species'), need: fd.getAll('need') });
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
