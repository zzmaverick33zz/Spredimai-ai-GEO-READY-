/* "Coloured by time": colour tones and the dated-samples chart (js/data/samples.js).
   The page is universal (many species), so the ages are shown as examples from the latest laboratory protocol.
   Draw-in animations run once on entry and are transform / opacity only. Reduced motion: drawn and still. */
(function () {
  'use strict';
  const { $, $$ } = BFF;
  const fmt = (n) => n.toLocaleString('en');
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  function render(sec) {
    const D = window.BFF_SAMPLES; if (!D || !D.samples || !D.samples.length) return;
    const list = $('[data-samples-list]', sec), axis = $('[data-samples-axis]', sec), src = $('[data-samples-src]', sec);
    const max = D.scaleMax || Math.max(...D.samples.map((s) => s.bp)) * 1.1, pct = (v) => (v / max * 100).toFixed(1);
    list.innerHTML = D.samples.slice().sort((a, b) => b.bp - a.bp).map((s) => '<li style="--v:' + pct(s.bp) + ';--e:' + pct(s.err) + '"><span class="dates__n">' + esc(s.species) + ' <small>' + esc(s.id) + '</small></span><span class="dates__t" aria-hidden="true"><i class="dates__err"></i><i class="dates__dot"></i></span><span class="dates__v"><b>' + fmt(s.bp) + '</b> ± ' + s.err + ' BP</span></li>').join('');
    const ticks = []; for (let v = 0; v <= max; v += 1000) ticks.push(v);
    axis.innerHTML = ticks.map((v, i) => '<span style="left:' + pct(v) + '%">' + (v === 0 ? 'Today' : fmt(v) + (i === ticks.length - 1 ? ' years' : '')) + '</span>').join('');
    src.textContent = 'BP: years before 1950. ' + D.source;
  }
  BFF.fx.material = {
    init(opts) {
      const sec = $('#material'); if (!sec) return;
      if (!sec.dataset.rendered) { render(sec); sec.dataset.rendered = '1'; }
      if (opts && opts.still) return;
      const gsap = window.gsap, once = (el, fn, start = 'top 82%') => el && window.ScrollTrigger.create({ trigger: el, start, once: true, onEnter: fn });
      once($('.tones'), () => {
        gsap.from($$('.tone'), { opacity: 0, y: 48, duration: 1.1, ease: 'power3.out', stagger: 0.16 });
        gsap.fromTo($('.tones__line b'), { scaleX: 0 }, { scaleX: 1, duration: 1.8, ease: 'power2.inOut', delay: 0.2 });
      });
      once($('.dates', sec), () => $$('.dates li', sec).forEach((li, i) => {
        gsap.fromTo([$('.dates__err', li), $('.dates__dot', li)], { scaleX: 0 }, { scaleX: 1, duration: 1.6, ease: 'power3.out', delay: 0.15 * i });
        gsap.from([$('.dates__n', li), $('.dates__v', li)], { opacity: 0, y: 12, duration: 0.9, ease: 'power3.out', delay: 0.15 * i });
      }), 'top 85%');
    }
  };
})();
