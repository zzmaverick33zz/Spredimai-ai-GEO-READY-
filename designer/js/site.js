/* Designer variants (A dark, B editorial, C Swiss): shared behaviour. No GSAP, no scroll libraries: native smooth scroll, IntersectionObserver reveals.
   Data: js/data/samples.js (radiocarbon examples), js/data/spec.js (specification rows, documents). */
(function () {
  'use strict';
  const { $, $$ } = BFF;
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const fmt = (n) => n.toLocaleString('en');
  const root = document.documentElement;
  if (!BFF.reduce) root.classList.add('js');

  /* ---------- header, drawer ---------- */
  const hdr = $('#hdr'), btn = $('#menuBtn'), drawer = $('#drawer');
  const onScroll = () => hdr && hdr.classList.toggle('is-solid', scrollY > 40);
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  const setMenu = (open) => { drawer.hidden = !open; btn.setAttribute('aria-expanded', String(open)); btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu'); root.style.overflow = open ? 'hidden' : ''; };
  if (btn && drawer) {
    btn.addEventListener('click', () => setMenu(drawer.hidden));
    drawer.addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !drawer.hidden) { setMenu(false); btn.focus(); } });
  }
  document.addEventListener('click', (e) => {                       // in-page links: smooth, then focus the target for keyboard and screen-reader users
    const a = e.target.closest('a[href^="#"]'); if (!a || a.getAttribute('href') === '#') return;
    const t = $(a.getAttribute('href')); if (!t) return;
    e.preventDefault(); t.scrollIntoView({ behavior: BFF.reduce ? 'auto' : 'smooth', block: 'start' });
    history.replaceState(null, '', a.getAttribute('href')); t.setAttribute('tabindex', '-1'); t.focus({ preventScroll: true });
  });

  /* ---------- videos: start after load, play only while visible ---------- */
  const vio = new IntersectionObserver((es) => es.forEach((e) => { const v = e.target; if (e.isIntersecting) { v.preload = 'auto'; const p = v.play(); if (p && p.catch) p.catch(() => {}); } else v.pause(); }), { threshold: 0.12, rootMargin: '10% 0px' });
  const arm = () => $$('video').forEach((v) => { if (BFF.reduce) v.pause(); else vio.observe(v); });
  if (document.readyState === 'complete') setTimeout(arm, 250); else addEventListener('load', () => setTimeout(arm, 250), { once: true });

  /* ---------- reveals ---------- */
  const rio = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('is-in'); rio.unobserve(e.target); } }), { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
  $$('.rv').forEach((el) => rio.observe(el));

  /* ---------- projects reel: buttons and mouse drag ---------- */
  const reel = $('#reel');
  if (reel) {
    $$('.reel-nav button').forEach((b) => b.addEventListener('click', () => reel.scrollBy({ left: Number(b.dataset.dir) * reel.clientWidth * 0.8, behavior: BFF.reduce ? 'auto' : 'smooth' })));
    let down = false, sx = 0, sl = 0, moved = false;
    reel.addEventListener('pointerdown', (e) => { if (e.pointerType !== 'mouse') return; down = true; moved = false; sx = e.clientX; sl = reel.scrollLeft; reel.style.scrollSnapType = 'none'; });
    addEventListener('pointermove', (e) => { if (!down) return; const dx = e.clientX - sx; if (Math.abs(dx) > 4) moved = true; reel.scrollLeft = sl - dx; });
    addEventListener('pointerup', () => { if (!down) return; down = false; reel.style.scrollSnapType = ''; });
    reel.addEventListener('click', (e) => { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
  }

  /* ---------- products accordion ---------- */
  const items = $$('.mk__item');
  items.forEach((it) => $('.mk__row', it).addEventListener('click', () => {
    const open = !it.classList.contains('is-open');
    items.forEach((o) => { o.classList.remove('is-open'); $('.mk__row', o).setAttribute('aria-expanded', 'false'); });
    if (open) { it.classList.add('is-open'); $('.mk__row', it).setAttribute('aria-expanded', 'true'); }
  }));

  /* ---------- annotated image ---------- */
  const pts = $$('.hot__pt'), notes = $$('.hot__list li');
  if (pts.length) {
    const show = (i) => { pts.forEach((p, k) => { p.classList.toggle('is-on', k === i); p.setAttribute('aria-expanded', String(k === i)); }); notes.forEach((l, k) => l.classList.toggle('is-on', k === i)); };
    const hov = () => matchMedia('(hover:hover)').matches;
    pts.forEach((p, i) => { p.addEventListener('click', () => show(i)); p.addEventListener('mouseenter', () => hov() && show(i)); });
    notes.forEach((l, i) => l.addEventListener('mouseenter', () => hov() && show(i)));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') show(-1); });
    show(0);
  }

  /* ---------- species discs: growth rings ---------- */
  const ringPath = (k, n = 36) => {
    const r0 = 7 + k * 5.2, p = [];
    for (let i = 0; i < n; i++) { const a = (i / n) * Math.PI * 2, w = 1 + 0.06 * Math.sin(3 * a + k * 1.7) + 0.04 * Math.sin(5 * a + k * 2.9); p.push([Math.cos(a) * r0 * w, Math.sin(a) * r0 * w]); }
    let d = 'M' + p[0].map((v) => v.toFixed(1)).join(',');
    for (let i = 0; i < n; i++) { const a = p[(i - 1 + n) % n], b = p[i], c = p[(i + 1) % n], e = p[(i + 2) % n]; d += 'C' + [b[0] + (c[0] - a[0]) / 6, b[1] + (c[1] - a[1]) / 6, c[0] - (e[0] - b[0]) / 6, c[1] - (e[1] - b[1]) / 6, c[0], c[1]].map((v) => v.toFixed(1)).join(','); }
    return d + 'Z';
  };
  $$('.spc__rings').forEach((svg) => { for (let k = 0; k < 8; k++) { const p = document.createElementNS('http://www.w3.org/2000/svg', 'path'); p.setAttribute('d', ringPath(k)); p.setAttribute('pathLength', '1'); svg.append(p); } });

  /* ---------- radiocarbon data: age scale and dated-samples chart ---------- */
  const D = window.BFF_SAMPLES;
  if (D && D.samples) {
    const max = D.scaleMax, pct = (v) => (v / max * 100).toFixed(1);
    $$('[data-age]').forEach((box) => {
      const bar = $('.age__bar', box), axis = $('.age__axis', box);
      D.samples.forEach((s) => { const d = document.createElement('i'); d.className = 'age__dot'; d.style.left = pct(s.bp) + '%'; const t = document.createElement('span'); t.textContent = fmt(s.bp); d.append(t); bar.append(d); });
      const ticks = []; for (let v = 0; v <= max; v += 1000) ticks.push(v);
      axis.innerHTML = ticks.map((v, i) => '<span style="left:' + pct(v) + '%">' + (v === 0 ? 'Today' : fmt(v) + (i === ticks.length - 1 ? ' years' : '')) + '</span>').join('');
    });
    const list = $('[data-samples-list]'), axis = $('[data-samples-axis]'), src = $('[data-samples-src]');
    if (list) {
      list.innerHTML = D.samples.slice().sort((a, b) => b.bp - a.bp).map((s) => '<li style="--v:' + pct(s.bp) + ';--e:' + pct(s.err) + '"><span class="dates__n">' + esc(s.species) + ' <small>' + esc(s.id) + '</small></span><span class="dates__t" aria-hidden="true"><i class="dates__err"></i><i class="dates__dot"></i></span><span class="dates__v"><b>' + fmt(s.bp) + '</b> ± ' + s.err + ' BP</span></li>').join('');
      const ticks = []; for (let v = 0; v <= max; v += 1000) ticks.push(v);
      axis.innerHTML = ticks.map((v, i) => '<span style="left:' + pct(v) + '%">' + (v === 0 ? 'Today' : fmt(v) + (i === ticks.length - 1 ? ' years' : '')) + '</span>').join('');
      src.textContent = 'BP: years before 1950. ' + D.source;
      rio.observe(list.closest('.dates-wrap') || list);
    }
    const old = D.samples.reduce((m, s) => (s.bp > m.bp ? s : m), D.samples[0]);
    $$('[data-oldest]').forEach((el) => { el.textContent = fmt(old.bp); });
    $$('[data-oldest-line]').forEach((el) => { el.textContent = old.species.toLowerCase() + ', ' + fmt(old.bp) + ' ± ' + old.err + ' BP' + (old.cal ? ' (calibrated ' + old.cal + ')' : ''); });
  }

  /* ---------- form prefill ---------- */
  const prefill = (o) => {
    const f = $('#form'); if (!f) return;
    const tick = (name, val) => { const el = $$('input[name=' + name + ']', f).find((i) => i.value === val); if (el) el.checked = true; };
    if (o.species) tick('species', o.species);
    (o.need || []).forEach((n) => tick('need', n));
    if (o.text) { const m = f.elements.message; m.value = (m.value ? m.value.replace(/\s*$/, '') + '\n' : '') + o.text; }
  };
  const go = (sel) => { const t = $(sel); if (t) t.scrollIntoView({ behavior: BFF.reduce ? 'auto' : 'smooth' }); };

  /* ---------- specification toolkit ---------- */
  const S = window.BFF_SPEC, tabs = $('[data-spec-tabs]');
  if (S && tabs) {
    const rows = $('[data-spec-rows]'), title = $('[data-spec-title]'), note = $('[data-spec-note]'), kind = $('[data-spec-kind]'), tbc = $('[data-spec-tbc]'), docs = $('[data-docs]'), swatch = $('[data-spec-swatch]');
    const imgOf = { 'bog-oak': 's14-img', 'bog-ash': 's15-img', 'black-walnut': 's19-img', elm: 's17-img', oak: 's16-img', ash: 's18-img' };
    let cur = S.species[0].id;
    tabs.innerHTML = S.species.map((s) => '<button type="button" role="tab" id="tab-' + s.id + '" data-id="' + s.id + '" aria-selected="false" tabindex="-1">' + esc(s.name) + '</button>').join('');
    const render = (id, focus) => {
      cur = id; const s = S.species.find((x) => x.id === id);
      $$('button', tabs).forEach((b) => { const on = b.dataset.id === id; b.setAttribute('aria-selected', String(on)); b.tabIndex = on ? 0 : -1; if (on && focus) b.focus(); });
      if (kind) kind.textContent = s.ancient ? 'Ancient wood · carbon-dated' : 'From the forest';
      if (title) title.textContent = s.name + ' multilayer board';
      if (note) note.textContent = s.note || '';
      if (swatch) swatch.style.backgroundImage = 'url(media/' + imgOf[id] + '.webp)';
      const list = S.rows.filter((r) => !r.only || (r.only === 'ancient') === !!s.ancient);
      rows.innerHTML = list.map((r) => '<div class="spec__row"><dt>' + esc(r.k) + '</dt><dd>' + esc(r.v.replace('{colour}', s.colour || '')) + (r.tbc && !S.confirmed ? ' <em class="tbc">TBC</em>' : '') + '</dd></div>').join('');
      if (tbc) tbc.hidden = S.confirmed || !list.some((r) => r.tbc);
    };
    tabs.addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) render(b.dataset.id); });
    tabs.addEventListener('keydown', (e) => {
      const k = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key]; if (!k) return;
      const i = S.species.findIndex((s) => s.id === cur); render(S.species[(i + k + S.species.length) % S.species.length].id, true); e.preventDefault();
    });
    if (docs) {
      docs.innerHTML = S.docs.map((d) => '<li><button type="button" class="doc" data-doc="' + d.id + '"><span><b>' + esc(d.label) + '</b><em>' + esc(d.kind) + '</em></span><i aria-hidden="true">Ask</i></button></li>').join('');
      docs.addEventListener('click', (e) => { const b = e.target.closest('[data-doc]'); if (!b) return; const d = S.docs.find((x) => x.id === b.dataset.doc); prefill({ need: ['documents'], text: 'I would like to discuss: ' + d.label + '.' }); go('#consultation'); });
    }
    $$('[data-species]').forEach((b) => b.addEventListener('click', (e) => { if (b.tagName === 'A') e.preventDefault(); render(b.dataset.species); go('#specify'); }));
    $$('[data-prefill]').forEach((a) => a.addEventListener('click', () => {
      const o = { patterns: { need: ['patterns'] }, walls: { need: ['walls and ceilings'] }, stairs: { need: ['stairs'] }, tables: { need: ['tables and cellars'] }, spec: { species: cur.replace('-', ' '), text: 'I would like to discuss the ' + S.species.find((s) => s.id === cur).name + ' specification.' } }[a.dataset.prefill];
      if (o) prefill(o);
    }));
    render(cur);
  }

  /* ---------- environment tabs (variant C) ---------- */
  const et = $('[data-envtabs]');
  if (et) {
    const bs = $$('button', et), ps = $$('[data-envpanel]');
    const pick = (id, focus) => { bs.forEach((b) => { const on = b.dataset.env === id; b.setAttribute('aria-selected', String(on)); b.tabIndex = on ? 0 : -1; if (on && focus) b.focus(); }); ps.forEach((p) => { p.hidden = p.dataset.envpanel !== id; }); };
    et.addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) pick(b.dataset.env); });
    et.addEventListener('keydown', (e) => { const k = { ArrowRight: 1, ArrowLeft: -1 }[e.key]; if (!k) return; const i = bs.findIndex((b) => b.getAttribute('aria-selected') === 'true'); pick(bs[(i + k + bs.length) % bs.length].dataset.env, true); e.preventDefault(); });
    pick(bs[0].dataset.env);
  }

  /* ---------- cursor (growth rings) ---------- */
  if (BFF.fx.cursor) { try { BFF.fx.cursor.init(); } catch (err) { console.warn('[cursor]', err); } }

  /* ---------- consultation form ---------- */
  (function form() {
    const ENDPOINT = window.BFF_FORM_ENDPOINT || '';
    const f = $('#form'), done = $('#formDone'), note = $('#stubNote'); if (!f) return;
    if (ENDPOINT && note) note.remove();
    const err = document.createElement('p'); err.className = 'form-error'; err.setAttribute('role', 'alert'); err.hidden = true; f.querySelector('button[type=submit]').parentElement.append(err);
    f.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = f.elements.email, name = f.elements.name, ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim());
      email.closest('.field').classList.toggle('is-invalid', !ok); $('#f-email-err').hidden = ok;
      name.closest('.field').classList.toggle('is-invalid', !name.value.trim());
      if (!name.value.trim()) { name.focus(); return; } if (!ok) { email.focus(); return; }
      const fd = new FormData(f), payload = Object.assign({}, Object.fromEntries(fd), { species: fd.getAll('species'), need: fd.getAll('need') });
      const submit = f.querySelector('button[type=submit]'); submit.disabled = true; err.hidden = true;
      try {
        if (ENDPOINT) { const r = await fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }); if (!r.ok) throw new Error(String(r.status)); }
        else await new Promise((r) => setTimeout(r, 400));
        f.hidden = true; done.hidden = false; done.setAttribute('tabindex', '-1'); done.focus();
      } catch (_) { err.textContent = 'Something went wrong. Please try again or write to info@bffloors.com.'; err.hidden = false; submit.disabled = false; }
    });
  })();
})();
