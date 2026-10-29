/* "The journey": an optional, expandable story (six scene loops). It never takes over the scroll: the visitor opens it, watches or steps through,
   and closes it. Scenes advance by themselves (about 6 s each), pause on keyboard focus and with the pause button, and can be stepped with the buttons or the arrow keys.
   Only the current and the next scene are loaded. Reduced motion: no auto-advance. Videos are seamless loops (see process_scenes.py). */
(function () {
  'use strict';
  const { $, $$, clamp } = BFF;
  const AUTO = 6000;
  BFF.fx.journey = {
    init() {
      const sec = $('#journey'); if (!sec) return;
      const open = $('.jr__open', sec), panel = $('.jr__panel', sec), stage = $('.jr__stage', sec), bar = $('.jr__bar i', sec);
      const scenes = $$('.scene', stage), caps = $$('.dcap', stage), dots = $$('.ddot', stage), vids = scenes.map((s) => $('video', s)), N = scenes.length;
      const playBtn = $('[data-act=play]', stage);
      let cur = 0, timer = 0, paused = BFF.reduce, hovering = false, opened = false; const loaded = new Set();
      const load = (i) => { if (i < 0 || i >= N || loaded.has(i)) return; loaded.add(i); vids[i].preload = 'auto'; vids[i].load(); };
      const run = (v) => { const p = v.play(); if (p && p.catch) p.catch(() => {}); };
      const schedule = () => {
        clearTimeout(timer); bar.classList.remove('is-run'); void bar.offsetWidth;
        if (!opened || paused || hovering || BFF.reduce) { bar.style.animationPlayState = 'paused'; return; }
        bar.classList.add('is-run'); bar.style.animationPlayState = 'running';
        timer = setTimeout(() => go((cur + 1) % N), AUTO);
      };
      const go = (i, fromUser) => {
        i = (i + N) % N; const prev = cur; cur = i;
        scenes.forEach((s, k) => { s.classList.toggle('is-on', k === i); s.classList.toggle('is-prev', k === prev && k !== i); });
        caps.forEach((c, k) => c.classList.toggle('is-on', k === i));
        dots.forEach((d, k) => { d.classList.toggle('is-on', k === i); if (k === i) d.setAttribute('aria-current', 'true'); else d.removeAttribute('aria-current'); });
        load(i); try { vids[i].currentTime = 0; } catch (_) {} run(vids[i]); load(i + 1);
        clearTimeout(go.t); go.t = setTimeout(() => vids.forEach((x, k) => { if (k !== cur) { x.pause(); scenes[k].classList.remove('is-prev'); } }), 1500);
        schedule();
      };
      const setOpen = (on) => {
        opened = on; sec.classList.toggle('is-open', on); open.setAttribute('aria-expanded', String(on));
        if (on) { load(0); load(1); setTimeout(() => { stage.scrollIntoView({ behavior: BFF.reduce ? 'auto' : 'smooth', block: 'center' }); }, 120); go(0); }
        else { clearTimeout(timer); vids.forEach((v) => v.pause()); bar.classList.remove('is-run'); open.focus({ preventScroll: true }); }
      };
      open.addEventListener('click', () => setOpen(!opened));
      stage.addEventListener('click', (e) => {
        const b = e.target.closest('[data-act]'); if (!b) return;
        const a = b.dataset.act;
        if (a === 'next') go(cur + 1, true); else if (a === 'prev') go(cur - 1, true);
        else if (a === 'close') setOpen(false);
        else if (a === 'play') { paused = !paused; playBtn.setAttribute('aria-pressed', String(paused)); playBtn.setAttribute('aria-label', paused ? 'Play' : 'Pause'); playBtn.textContent = paused ? '▶' : '❚❚'; schedule(); }
      });
      dots.forEach((d, i) => d.addEventListener('click', () => go(i, true)));
      stage.addEventListener('focusin', () => { hovering = true; schedule(); });
      stage.addEventListener('focusout', () => { hovering = false; schedule(); });
      sec.addEventListener('keydown', (e) => { if (!opened) return; if (e.key === 'ArrowRight') { go(cur + 1, true); e.preventDefault(); } else if (e.key === 'ArrowLeft') { go(cur - 1, true); e.preventDefault(); } else if (e.key === 'Escape') setOpen(false); });
      new IntersectionObserver((es) => es.forEach((e) => { if (!e.isIntersecting && opened) { vids.forEach((v) => v.pause()); clearTimeout(timer); } else if (e.isIntersecting && opened) { run(vids[cur]); schedule(); } }), { threshold: 0.05 }).observe(stage);
      if (BFF.reduce) { playBtn.setAttribute('aria-pressed', 'true'); playBtn.textContent = '▶'; playBtn.setAttribute('aria-label', 'Play'); }
    }
  };
})();
