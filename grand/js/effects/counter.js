/* Effect 4: carbon-dating counter and heritage numbers.
   Behaviour modelled on 21st.dev "Number Ticker" (dev.yadhakim; each digit rolls independently, the leading digit starts first,
   the ones digit resolves last, scroll-triggered on viewport entry) with the rolling-digit look of "Stats Section with Odometer
   Numbers" (kedhareswer, MIT). Sources need an API key and could not be read; written from the documented behaviour.
   Data: #ch4 .dated[data-years]. There is NO confirmed age yet, so data-years is empty and the digits settle on dashes.
   TODO: confirm with client. When the carbon-dating result is known, put it in data-years (digits only) and nothing else changes.
   Screen readers get the final value once (aria-label, aria-live off), not every tick. */
(function () {
  'use strict';
  const { $, $$ } = BFF;
  const DASH = 10;                                         // strip index of the placeholder dash

  /** Builds one rolling column. target: 0-9 or DASH. Returns { el, strip, to } where to = final strip index. */
  function column(target, spins) {
    const col = document.createElement('span'); col.className = 'odo'; col.setAttribute('aria-hidden', 'true');
    const strip = document.createElement('span'); strip.className = 'odo__strip';
    const n = spins * 10 + (target === DASH ? 10 : target);
    for (let k = 0; k <= n; k++) { const i = document.createElement('i'); i.textContent = target === DASH && k === n ? '–' : String(k % 10); strip.append(i); }
    col.append(strip);
    return { el: col, strip, to: n };
  }

  function build(host, digits, still) {                    // digits: array of 0-9 or DASH
    host.textContent = '';
    const cols = digits.map((d, i) => column(d, 1 + Math.floor(i / 2)));
    cols.forEach((c, i) => {
      if (i > 0 && (cols.length - i) % 3 === 0 && cols.length > 3) { const s = document.createElement('span'); s.className = 'odo__sep'; s.textContent = ','; s.setAttribute('aria-hidden', 'true'); host.append(s); }
      host.append(c.el);
    });
    cols.forEach((c) => c.strip.style.setProperty('--d', still ? c.to : 0));
    return cols;
  }
  function play(cols, extra) {
    const gsap = window.gsap, tl = gsap.timeline();
    cols.forEach((c, i) => tl.to(c.strip, { '--d': c.to, duration: 1.9 + i * 0.22, ease: 'power4.out' }, i * 0.12));   // left starts first, right resolves last
    if (extra) tl.add(extra, 0);
    return tl;
  }

  function dated(still) {
    const box = $('.dated'); if (!box) return;
    const count = $('.dated__count', box), fill = $('.dated__line i', box);
    const raw = (box.dataset.years || '').replace(/\D/g, '');
    const digits = raw ? raw.split('').map(Number) : [DASH, DASH, DASH, DASH];
    count.setAttribute('aria-label', raw ? Number(raw).toLocaleString('en') + ' years' : 'Age pending the radiocarbon result');
    count.setAttribute('role', 'img'); count.setAttribute('aria-live', 'off');
    const cols = build(count, digits, still);
    if (still) { fill.style.transform = 'scaleX(1)'; return; }
    const gsap = window.gsap;
    fill.style.transform = 'scaleX(0)';
    window.ScrollTrigger.create({ trigger: box, start: 'top 85%', once: true, onEnter: () => {
      play(cols, gsap.fromTo(fill, { scaleX: 0 }, { scaleX: 1, duration: 3.2, ease: 'power3.out' }));
    } });
  }

  function facts(still) {
    $$('#heritage .fact b').forEach((b) => {
      const m = b.textContent.trim().match(/^(\D*)(\d+)(\D*)$/); if (!m) return;      // "3rd", "20+"; leaves "LT . ES" alone
      const label = b.textContent.trim();
      const sr = document.createElement('span'); sr.className = 'sr-only'; sr.textContent = label;
      const num = document.createElement('span'); num.setAttribute('aria-hidden', 'true'); num.className = 'odo__num';
      const cols = m[2].split('').map((d) => column(Number(d), 1));
      if (m[1]) num.append(m[1]);
      cols.forEach((c) => { num.append(c.el); c.strip.style.setProperty('--d', still ? c.to : 0); });
      if (m[3]) num.append(m[3]);
      b.textContent = ''; b.append(sr, num);
      if (!still) window.ScrollTrigger.create({ trigger: b, start: 'top 88%', once: true, onEnter: () => play(cols) });
    });
  }

  BFF.fx.counter = { init(opts) { const still = !!(opts && opts.still); dated(still); facts(still); } };
})();
