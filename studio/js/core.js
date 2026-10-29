/* Shared helpers for the page and its effects. Plain script, no build step. */
(function () {
  'use strict';
  const mq = (q) => window.matchMedia(q);
  const BFF = window.BFF = {
    fx: {},                                   // effects register themselves here: BFF.fx.name = { init() }
    $: (s, r = document) => r.querySelector(s),
    $$: (s, r = document) => Array.from(r.querySelectorAll(s)),
    isStatic: new URLSearchParams(location.search).has('static'),   // ?static = no motion at all
    get reduce() { return this.isStatic || mq('(prefers-reduced-motion: reduce)').matches; },
    get coarse() { return mq('(pointer: coarse)').matches || !mq('(hover: hover)').matches; },
    clamp: (v, a, b) => Math.min(b, Math.max(a, v)),
    lerp: (a, b, t) => a + (b - a) * t,
    /** Calls onShow / onHide as an element enters / leaves the viewport. */
    whenVisible(el, onShow, onHide, margin = '0px') {
      const io = new IntersectionObserver((es) => es.forEach((e) => (e.isIntersecting ? onShow(e) : onHide && onHide(e))), { rootMargin: margin });
      io.observe(el); return io;
    },
    /** Pointer position inside an element, in CSS px. */
    local(el, e) { const r = el.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top, w: r.width, h: r.height }; }
  };
})();
