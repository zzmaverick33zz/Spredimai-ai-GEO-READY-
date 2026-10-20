import './styles/main.css';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from 'lenis';
import { hydrateMedia } from './js/media.js';
import { initForm } from './js/form.js';

document.documentElement.classList.add('js');
gsap.registerPlugin(ScrollTrigger);

const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

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
  const a = first.offsetTop, b = last.offsetTop;
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
}

const mm = gsap.matchMedia();
mm.add('(prefers-reduced-motion: no-preference)', () => {
  heroIntro();
  if (innerWidth >= 900) lift();   // pin first: later triggers must measure after its spacer
  colourByDepth();
  reveals();
  parallax();
});
// reduced motion: still tween nothing; chapters keep their own grounds
mm.add('(prefers-reduced-motion: reduce)', () => {
  document.documentElement.classList.remove('js');
});

/* ---------- media, form ---------- */
hydrateMedia().then(() => { watchVideos(); ScrollTrigger.refresh(); });
initForm();
