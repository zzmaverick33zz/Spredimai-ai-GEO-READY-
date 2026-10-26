/* Effect 5: before / after slider on the first cut.
   Behaviour modelled on 21st.dev "Image Compare" (mohammadshehadeh, MIT): a draggable divider, optional hover-follow on desktop,
   keyboard-accessible, horizontal or vertical. The source needs an API key and could not be read; this follows its documented
   behaviour: pointer drag with capture, arrow keys move 2 %, Home / End jump to the ends, role="slider" with aria-valuenow.
   Markup: .compare[data-compare] > .compare__after + .compare__before (clipped) ; options: data-hover="true", data-orientation. */
(function () {
  'use strict';
  const { $$, clamp } = BFF;
  const STEP = 2;

  function setup(root) {
    const before = root.querySelector('.compare__before'), handle = root.querySelector('.compare__handle');
    const vertical = root.dataset.orientation === 'vertical';
    let pos = clamp(parseFloat(root.dataset.start) || 50, 0, 100), dragging = false;
    const hoverFollow = root.dataset.hover === 'true' && matchMedia('(hover: hover) and (pointer: fine)').matches;
    const paint = () => {
      root.style.setProperty('--pos', pos + '%');
      before.style.clipPath = vertical ? `inset(0 0 ${100 - pos}% 0)` : `inset(0 ${100 - pos}% 0 0)`;
      handle.setAttribute('aria-valuenow', String(Math.round(pos)));
      handle.setAttribute('aria-valuetext', Math.round(pos) + '% ' + (root.dataset.labelBefore || 'before') + ', ' + (100 - Math.round(pos)) + '% ' + (root.dataset.labelAfter || 'after'));
    };
    const fromEvent = (e) => { const r = root.getBoundingClientRect(); pos = clamp(vertical ? ((e.clientY - r.top) / r.height) * 100 : ((e.clientX - r.left) / r.width) * 100, 0, 100); paint(); };
    root.addEventListener('pointerdown', (e) => { if (e.button > 0) return; dragging = true; root.setPointerCapture(e.pointerId); root.classList.add('is-drag'); fromEvent(e); handle.focus({ preventScroll: true }); });
    root.addEventListener('pointermove', (e) => { if (dragging || (hoverFollow && e.pointerType === 'mouse')) fromEvent(e); });
    const end = (e) => { if (!dragging) return; dragging = false; root.classList.remove('is-drag'); try { root.releasePointerCapture(e.pointerId); } catch (_) {} };
    root.addEventListener('pointerup', end); root.addEventListener('pointercancel', end);
    handle.addEventListener('keydown', (e) => {
      const dec = vertical ? 'ArrowUp' : 'ArrowLeft', inc = vertical ? 'ArrowDown' : 'ArrowRight';
      let used = true;
      if (e.key === dec || (!vertical && e.key === 'ArrowDown') || (vertical && e.key === 'ArrowLeft')) pos = clamp(pos - STEP, 0, 100);
      else if (e.key === inc || (!vertical && e.key === 'ArrowUp') || (vertical && e.key === 'ArrowRight')) pos = clamp(pos + STEP, 0, 100);
      else if (e.key === 'Home') pos = 0; else if (e.key === 'End') pos = 100; else used = false;
      if (used) { e.preventDefault(); paint(); }
    });
    // gentle invitation once, when it first appears (skipped for reduced motion)
    if (!BFF.reduce && window.gsap) BFF.whenVisible(root, function once(e) {
      if (root._shown) return; root._shown = true; const o = { v: pos };
      window.gsap.timeline().to(o, { v: 62, duration: 0.9, ease: 'power2.inOut', onUpdate: () => { pos = o.v; paint(); } })
        .to(o, { v: 50, duration: 0.9, ease: 'power2.inOut', onUpdate: () => { pos = o.v; paint(); } });
    });
    paint();
  }

  BFF.fx.compare = { init() { $$('[data-compare]').forEach(setup); } };
})();
