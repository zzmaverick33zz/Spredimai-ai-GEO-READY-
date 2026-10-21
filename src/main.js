import './styles/main.css';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from 'lenis';
import { hydrateMedia } from './js/media.js';
import { initForm } from './js/form.js';

document.documentElement.classList.add('js');
gsap.registerPlugin(ScrollTrigger);

// ?static renders the page with no motion at all (for design import / screenshots)
const isStatic = new URLSearchParams(location.search).has('static');
const reduce = isStatic || matchMedia('(prefers-reduced-motion: reduce)').matches;
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

// 3D beats only where there is WebGL, motion is allowed and data saving is off; otherwise they stay hidden
const webgl = (() => { try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch { return false; } })();
const use3d = !reduce && webgl && !navigator.connection?.saveData;
if (use3d) $$('.beat').forEach(b => { b.hidden = false; });

/* ---------- media brief toggle (#clean hides briefs) ---------- */
const toggle = $('#briefToggle');
const setBrief = on => {
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
const setMenu = open => {
  drawer.hidden = !open;
  btn.setAttribute('aria-expanded', String(open));
  btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  document.documentElement.style.overflow = open ? 'hidden' : '';
};
btn.addEventListener('click', () => setMenu(drawer.hidden));
drawer.addEventListener('click', e => { if (e.target.closest('a')) setMenu(false); });
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && !drawer.hidden) { setMenu(false); btn.focus(); }
});

/* ---------- projects reel ---------- */
const reel = $('#reel');
$$('.reel-nav button').forEach(b => b.addEventListener('click', () => {
  reel.scrollBy({ left: Number(b.dataset.dir) * reel.clientWidth * .8, behavior: reduce ? 'auto' : 'smooth' });
}));

/* ---------- video: pause off-screen, poster only on reduced motion ---------- */
const watchVideos = () => {
  const vio = new IntersectionObserver(es => es.forEach(e => {
    const v = e.target;
    e.isIntersecting ? v.play?.().catch(() => {}) : v.pause?.();
  }), { threshold: .15 });
  $$('.slot video').forEach(v => {
    if (reduce) { v.removeAttribute('autoplay'); v.pause(); } else vio.observe(v);
  });
};

/* ---------- smooth scroll ---------- */
let lenis = null;
if (!reduce) {
  lenis = new Lenis({ lerp: .09, wheelMultiplier: .9 });
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add(t => lenis.raf(t * 1000));
  gsap.ticker.lagSmoothing(0);
}
document.addEventListener('click', e => {
  const a = e.target.closest('a[href^="#"]');
  if (!a || a.getAttribute('href') === '#') return;
  const t = $(a.getAttribute('href'));
  if (!t) return;
  e.preventDefault();
  if (lenis) lenis.scrollTo(t, { offset: -70, duration: 1.4 });
  else t.scrollIntoView({ behavior: 'auto' });
  history.replaceState(null, '', a.getAttribute('href') === '#top' ? location.pathname + location.search : a.getAttribute('href'));
  t.setAttribute('tabindex', '-1'); t.focus({ preventScroll: true });
});

/* ---------- rail: active chapter + progress line (works without motion) ---------- */
const rail = $('#rail');
const links = $$('a', rail);
const targets = links.map(a => $(a.getAttribute('href')));
const first = targets[0], last = $('#arrival');
const rio = new IntersectionObserver(entries => entries.forEach(en => {
  if (en.isIntersecting) {
    const i = targets.indexOf(en.target);
    links.forEach((l, j) => { l.classList.toggle('is-active', i === j); if (i === j) l.setAttribute('aria-current', 'true'); else l.removeAttribute('aria-current'); });
  }
}), { rootMargin: '-45% 0px -50% 0px' });
targets.forEach(t => rio.observe(t));
const bar = $('.rail__bar > i', rail);
const railVis = () => {
  const y = window.scrollY + innerHeight / 2;
  const top = el => el.getBoundingClientRect().top + window.scrollY;
  const a = top(first), b = top(last);
  rail.classList.toggle('is-on', y > a && y < b + innerHeight * .4);
  bar.style.transform = `scaleY(${Math.min(1, Math.max(0, (y - a) / (b - a)))})`;
};
railVis();
window.addEventListener('scroll', railVis, { passive: true });

/* ---------- motion ---------- */
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();

function splitWords(el) {
  const walk = node => {
    [...node.childNodes].forEach(n => {
      if (n.nodeType === 3) {
        const frag = document.createDocumentFragment();
        n.textContent.split(/(\s+)/).forEach(w => {
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
  const h1 = $('#h-hero');
  const words = splitWords(h1);
  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
  tl.set('.hero__veil', { opacity: 1 })
    .to('.hero__veil', { opacity: 0, duration: 1.8, ease: 'power2.out' }, 0)
    .from(words, { yPercent: 110, duration: .9, stagger: .07 }, .35)
    .fromTo('.hero .slot img', { scale: 1.12 }, { scale: 1, duration: 7, ease: 'power2.out' }, 0)
    .from('.hero__ctas, .hero__facts', { autoAlpha: 0, y: 14, duration: .7, stagger: .12 }, .9);
}

function colourByDepth() {
  const colours = {
    silt: css('--silt'), deep: css('--deep'), peat: css('--peat'),
    char: css('--char'), oak: css('--oak'), linen: css('--linen')
  };
  const set = c => gsap.to(document.body, { backgroundColor: c, duration: .9, ease: 'power2.out', overwrite: 'auto' });
  const zones = [
    ...$$('.chapter').map(el => [el, colours[el.dataset.g]]),
    ...$$('.beat').filter(b => !b.hidden).map(el => [el, colours[el.dataset.g]]),
    [$('#ch3'), colours.peat]
  ];
  zones.forEach(([el, c]) => ScrollTrigger.create({
    trigger: el, start: 'top 60%', end: 'bottom 60%',
    onToggle: s => s.isActive && set(c)
  }));
}

function lift() {
  // the one pinned moment: the trunk rises into the light, ground shifts deep -> peat
  const sec = $('#ch3'), slot = $('.slot', sec);
  const tl = gsap.timeline({
    scrollTrigger: { trigger: sec, start: 'top top', end: '+=100%', pin: true, scrub: 1, anticipatePin: 1 }
  });
  tl.fromTo(slot, { yPercent: 16, scale: 1.14 }, { yPercent: 0, scale: 1, ease: 'none' }, 0)
    .fromTo(sec, { backgroundColor: css('--deep') }, { backgroundColor: css('--peat'), ease: 'none' }, 0)
    .fromTo($$('.interlude__body > *', sec), { y: 40, autoAlpha: 0 }, { y: 0, autoAlpha: 1, stagger: .15, ease: 'power2.out' }, .35);
}

function parallax() {
  $$('.chapter__media').forEach(m => {
    const main = $('.slot--main, .slot--wide', m), detail = $('.slot--detail', m);
    const run = (el, from, to) => el && gsap.fromTo(el, { yPercent: from }, {
      yPercent: to, ease: 'none',
      scrollTrigger: { trigger: m, start: 'top bottom', end: 'bottom top', scrub: true }
    });
    run(main, 5, -5);
    run(detail, 12, -4);   // detail drifts later than the main frame
  });
  $$('.arrival .slot, .heritage .slot').forEach(s => gsap.fromTo(s, { yPercent: 6 }, {
    yPercent: -6, ease: 'none', scrollTrigger: { trigger: s, start: 'top bottom', end: 'bottom top', scrub: true }
  }));
}

function reveals() {
  $$('.chapter__text, .arrival__head, .sec-head').forEach(el => gsap.from(el.children, {
    autoAlpha: 0, y: 24, duration: .8, ease: 'power3.out', stagger: .1,
    scrollTrigger: { trigger: el, start: 'top 82%', once: true }
  }));
  // headings rise out of a mask, word by word; split only when the heading is about to enter
  $$('.chapter h3, .sec-head h2, .arrival h2, .statement h2, .heritage h2, .consult h2').forEach(h => {
    ScrollTrigger.create({
      trigger: h, start: 'top 97%', once: true,
      onEnter: () => gsap.from(splitWords(h), { yPercent: 115, duration: 1, ease: 'power3.out', stagger: .06 })
    });
  });
  // photographs open like a curtain once; only those below the fold start closed
  const slots = $$('.chapter__media .slot, .arrival .slot, .heritage .slot, .proj .slot, .prod .slot, .sp .slot');
  const below = slots.filter(sl => sl.getBoundingClientRect().top > innerHeight * .92);
  gsap.set(below, { clipPath: 'inset(0 0 100% 0)' });
  ScrollTrigger.batch(below, {
    start: 'top 92%', once: true,
    onEnter: els => gsap.to(els, { clipPath: 'inset(0 0 0% 0)', duration: 1.2, ease: 'power3.out', stagger: .08, clearProps: 'clipPath' })
  });
}

/* hero: silt drifting in the water */
function silt() {
  const cv = $('.silt'); if (!cv) return;
  const ctx = cv.getContext('2d'); let w = 0, h = 0, raf = 0, on = false;
  const N = innerWidth < 760 ? 38 : 80, ps = [];
  const size = () => { const r = cv.getBoundingClientRect(); w = cv.width = r.width; h = cv.height = r.height; };
  size(); addEventListener('resize', size);
  for (let i = 0; i < N; i++) ps.push({ x: Math.random(), y: Math.random(), r: .6 + Math.random() * 1.8, s: .02 + Math.random() * .05, a: .12 + Math.random() * .4, ph: Math.random() * 6.3 });
  const draw = t => {
    ctx.clearRect(0, 0, w, h);
    for (const p of ps) {
      p.y -= p.s * .004; if (p.y < -.02) { p.y = 1.02; p.x = Math.random(); }
      const x = (p.x + Math.sin(t * .0003 + p.ph) * .015) * w, y = p.y * h;
      ctx.beginPath(); ctx.arc(x, y, p.r, 0, 6.283); ctx.fillStyle = `rgba(190,225,222,${p.a})`; ctx.fill();
    }
    raf = on ? requestAnimationFrame(draw) : 0;
  };
  new IntersectionObserver(es => { on = es[0].isIntersecting; if (on && !raf) raf = requestAnimationFrame(draw); }).observe(cv);
}

/* the wood's journey in 3D: one scalar t drives the trunk across six beats */
function journey3D() {
  const beats = $$('.beat').filter(b => !b.hidden), canvas = $('#gl');
  if (!use3d || !beats.length) return;
  let api = null, loading = false;
  const boot = async () => {
    if (api || loading) return; loading = true;
    await new Promise(r => (window.requestIdleCallback || setTimeout)(r, { timeout: 600 }));
    try {
      const m = await import('./js/scene.js');
      api = await m.createScene(canvas); window.__bff = api;
    } catch (e) {
      console.warn('3D disabled', e); beats.forEach(b => { b.hidden = true; }); ScrollTrigger.refresh();
    }
  };
  new IntersectionObserver((es, o) => { if (es.some(e => e.isIntersecting)) { boot(); o.disconnect(); } }, { rootMargin: '60% 0px' }).observe(beats[0]);
  const clamp = v => Math.min(1, Math.max(0, v));
  gsap.ticker.add(() => {
    if (!api) return;
    const vh = window.innerHeight; let t = null, op = 0;
    beats.forEach((b, i) => {
      const r = b.getBoundingClientRect();
      if (r.top < vh && r.bottom > 0) {
        t = i + clamp(-r.top / (r.height - vh));
        op = Math.max(op, Math.min(clamp((vh - r.top) / (vh * .45)), clamp((r.bottom - vh * .3) / (vh * .4))));
      }
    });
    const on = t !== null && op > .01;
    canvas.classList.toggle('is-on', on); canvas.style.opacity = on ? op : 0;
    if (on) api.setT(t);
    api.setLive(on);
  });
}

const mm = gsap.matchMedia();
mm.add(isStatic ? '(max-width: 0px)' : '(prefers-reduced-motion: no-preference)', () => {
  heroIntro();
  if (innerWidth >= 900) lift();   // pin first: later triggers must measure after its spacer
  colourByDepth();
  reveals();
  parallax();
  silt();
  journey3D();
});
// reduced motion: still tween nothing; chapters keep their own grounds
mm.add(isStatic ? '(min-width: 0px)' : '(prefers-reduced-motion: reduce)', () => {
  document.documentElement.classList.remove('js');
});

/* ---------- media, form ---------- */
hydrateMedia().then(() => { watchVideos(); ScrollTrigger.refresh(); });
initForm();
