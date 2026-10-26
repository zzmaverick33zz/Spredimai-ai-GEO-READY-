/* Effect 2: the diver's torch.
   Behaviour modelled on 21st.dev "Torch Reveal" (rmahammad, MIT): a cursor-tracked soft mask wipes a hidden layer into view.
   The source needs an API key and could not be read; this is written from the documented behaviour.
   Here the "hidden layer" is the lit image itself and the mask is a dark scrim with a soft hole that follows the pointer
   with a little lag. Never covers copy: it lives inside media slots only.
   Options on the .slot: data-torch (enable), data-torch-radius (px, default 220), data-torch-dim="light" (for slots on pale sections).
   Touch and idle: the hole drifts along a slow Lissajous path. Reduced motion: no scrim, the image is simply lit. */
(function () {
  'use strict';
  const { $$, reduce, clamp, lerp } = BFF;
  const active = new Set(); let raf = 0;

  function loop(ts) {
    raf = 0;
    active.forEach((T) => {
      const t = ts / 1000, r = T.rect;
      if (!T.hover) {                                         // idle / touch: Lissajous drift, each slot on its own phase
        T.tx = r.w * (0.5 + 0.28 * Math.sin(t * 0.43 + T.ph)); T.ty = r.h * (0.5 + 0.25 * Math.sin(t * 0.31 + T.ph * 1.7));
      }
      T.x = lerp(T.x, T.tx, 0.12); T.y = lerp(T.y, T.ty, 0.12);
      T.rad = lerp(T.rad, T.hover ? T.radius : T.radius * 0.8, 0.08);
      T.el.style.setProperty('--x', T.x.toFixed(1) + 'px'); T.el.style.setProperty('--y', T.y.toFixed(1) + 'px'); T.el.style.setProperty('--r', T.rad.toFixed(1) + 'px');
    });
    if (active.size) raf = requestAnimationFrame(loop);
  }
  const kick = () => { if (!raf && active.size) raf = requestAnimationFrame(loop); };

  function setup(slot, i) {
    const el = document.createElement('span'); el.className = 'torch'; el.setAttribute('aria-hidden', 'true');
    if (slot.dataset.torchDim === 'light') el.classList.add('torch--light');
    el.innerHTML = '<span class="torch__dim"></span><span class="torch__glow"></span>';
    slot.append(el);
    const base = parseFloat(slot.dataset.torchRadius) || 220;
    const T = { el, x: 0, y: 0, tx: 0, ty: 0, hover: false, ph: i * 1.9, rect: { w: 1, h: 1 }, radius: 220, rad: 220 };
    const measure = () => { const b = slot.getBoundingClientRect(); T.rect = { w: b.width, h: b.height }; T.radius = clamp(base, 90, 0.85 * Math.min(b.width, b.height)); if (!T.x) { T.x = T.tx = b.width / 2; T.y = T.ty = b.height / 2; T.rad = T.radius; } };
    measure(); new ResizeObserver(measure).observe(slot);
    slot.addEventListener('pointermove', (e) => {
      if (e.pointerType === 'touch') return;
      const p = BFF.local(slot, e); T.hover = true; T.tx = p.x; T.ty = p.y;
    }, { passive: true });
    slot.addEventListener('pointerleave', () => { T.hover = false; });
    // touch: follow a finger that rests on the slot (scrolling cancels the pointer, then the drift takes over)
    slot.addEventListener('pointerdown', (e) => { if (e.pointerType === 'touch') { const p = BFF.local(slot, e); T.hover = true; T.tx = p.x; T.ty = p.y; } }, { passive: true });
    slot.addEventListener('pointerup', (e) => { if (e.pointerType === 'touch') T.hover = false; });
    slot.addEventListener('pointercancel', () => { T.hover = false; });
    BFF.whenVisible(slot, () => { active.add(T); kick(); }, () => { active.delete(T); });
  }

  BFF.fx.torch = {
    init() {
      if (reduce) return;                                     // no scrim at all: the lit image is the final state
      $$('[data-torch]').forEach(setup);
    }
  };
})();
