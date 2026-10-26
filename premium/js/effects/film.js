/* "The descent, in one take": a pinned section where SCROLL CONTROLS THE FILM (the video's time follows the scroll).
   Smoothness: the clip is encoded with a keyframe every 6 frames, the target time is eased, and a new seek is only
   issued after the previous one finished ("seeked"), so seeks never queue up. Only transform / opacity are animated.
   Fallbacks: reduced motion / ?static -> poster + first caption, no pin. Video that cannot load -> poster. */
(function () {
  'use strict';
  const { $, $$, clamp } = BFF;
  BFF.fx.film = {
    init() {
      const sec = $('#film'); if (!sec) return;
      const v = $('.film__video', sec), caps = $$('.film__cap', sec), dot = $('.film__gauge b', sec), hint = $('.film__hint', sec);
      const gsap = window.gsap, ST = window.ScrollTrigger;
      const from = caps.map((c) => parseFloat(c.dataset.from));
      // relative depth over film time (0 surface .. 1 deep): the lake and forest are up, the water is down, the pull brings it back
      const depthAt = (t) => (t < 12 ? 0 : t < 16 ? (t - 12) / 4 : t < 27 ? 1 : t < 31 ? 1 - (t - 27) / 4 : 0);
      let dur = 37.6, target = 0, cur = 0, seeking = false, active = false, ready = false, lastCap = -1;
      const setCap = (t) => { let k = 0; from.forEach((f, i) => { if (t >= f) k = i; }); if (k !== lastCap) { caps.forEach((c, i) => c.classList.toggle('is-on', i === k)); lastCap = k; } };
      const seekTo = (t) => { seeking = true; try { v.currentTime = t; } catch (_) { seeking = false; } };
      v.addEventListener('seeked', () => { seeking = false; });
      const tick = () => {
        if (!active || !ready) return;
        cur += (target - cur) * 0.2;
        if (Math.abs(target - cur) < 0.004) cur = target;
        if (!seeking && Math.abs(v.currentTime - cur) > 0.03) seekTo(cur);
        setCap(cur); dot.style.transform = 'translate3d(0,' + (depthAt(cur) * 91).toFixed(1) + 'px,0)';
      };
      const start = () => {
        ST.create({
          trigger: sec, start: 'top top', end: () => '+=' + Math.round(innerHeight * (innerWidth < 760 ? 3.4 : 4.2)), pin: true, anticipatePin: 1,
          onUpdate: (self) => { target = self.progress * (dur - 0.08); if (self.progress > 0.02 && hint) hint.style.opacity = 0; else if (hint) hint.style.opacity = 1; },
          onToggle: (self) => { active = self.isActive || self.progress > 0; if (!self.isActive && self.progress === 1) { target = dur - 0.08; } }
        });
        gsap.ticker.add(tick);
        setCap(0);
      };
      v.pause();
      dur = 37.6;                                   // known length of the cut: the pin (and the page height) never depend on the download
      start();
      v.addEventListener('loadedmetadata', () => { if (v.duration) dur = v.duration; });
      v.addEventListener('error', () => { sec.classList.add('film--poster'); });
      // download it only when the visitor is about to arrive (keeps the first paint light)
      new IntersectionObserver((es, o) => { if (es.some((e) => e.isIntersecting)) { v.preload = 'auto'; v.load(); ready = true; o.disconnect(); } }, { rootMargin: '70% 0px' }).observe(sec);
    }
  };
})();
