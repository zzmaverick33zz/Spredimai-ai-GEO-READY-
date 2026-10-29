/* Studio build: products accordion, annotated material image, species rings, specification toolkit, hero age scale, form prefill.
   Everything here works without motion. Data: js/data/samples.js and js/data/spec.js. */
(function () {
  'use strict';
  const { $, $$ } = BFF;
  const NS = 'http://www.w3.org/2000/svg';
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  /* ---------- products accordion (one open at a time) ---------- */
  function accordion() {
    const items = $$('.mk__item');
    items.forEach((it) => $('.mk__row', it).addEventListener('click', () => {
      const open = !it.classList.contains('is-open');
      items.forEach((o) => { o.classList.remove('is-open'); $('.mk__row', o).setAttribute('aria-expanded', 'false'); });
      if (open) { it.classList.add('is-open'); $('.mk__row', it).setAttribute('aria-expanded', 'true'); }
    }));
  }

  /* ---------- annotated material image ---------- */
  function hotspots() {
    const pts = $$('.hot__pt'), list = $$('.hot__list li');
    const show = (i) => { pts.forEach((p, k) => { p.classList.toggle('is-on', k === i); p.setAttribute('aria-expanded', String(k === i)); }); list.forEach((l, k) => l.classList.toggle('is-on', k === i)); };
    pts.forEach((p, i) => { p.addEventListener('click', () => show(i)); p.addEventListener('mouseenter', () => { if (matchMedia('(hover:hover)').matches) show(i); }); });
    list.forEach((l, i) => l.addEventListener('mouseenter', () => { if (matchMedia('(hover:hover)').matches) show(i); }));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') show(-1); });
    show(0);
  }

  /* ---------- growth rings over each species disc (original drawing, same family as the cursor) ---------- */
  function rings() {
    const ringPath = (k, n = 36) => {
      const r0 = 7 + k * 5.2, pts = [];
      for (let i = 0; i < n; i++) { const a = (i / n) * Math.PI * 2, w = 1 + 0.06 * Math.sin(3 * a + k * 1.7) + 0.04 * Math.sin(5 * a + k * 2.9); pts.push([Math.cos(a) * r0 * w, Math.sin(a) * r0 * w]); }
      let d = 'M' + pts[0].map((v) => v.toFixed(1)).join(',');
      for (let i = 0; i < n; i++) { const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n]; d += 'C' + [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6, p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6, p2[0], p2[1]].map((v) => v.toFixed(1)).join(','); }
      return d + 'Z';
    };
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } }), { threshold: 0.4 });
    $$('.spc li').forEach((li) => io.observe(li));
    $$('.spc__rings').forEach((svg) => { for (let k = 0; k < 8; k++) { const p = document.createElementNS(NS, 'path'); p.setAttribute('d', ringPath(k)); p.setAttribute('pathLength', '1'); svg.append(p); } });
  }

  /* ---------- hero age scale, from js/data/samples.js ---------- */
  function age() {
    const box = $('[data-age]'), D = window.BFF_SAMPLES; if (!box || !D) return;
    const max = D.scaleMax, bar = $('.age__bar', box), axis = $('.age__axis', box);
    D.samples.forEach((s) => { const d = document.createElement('i'); d.className = 'age__dot'; d.style.left = (s.bp / max * 100).toFixed(2) + '%'; d.title = s.species + ' ' + s.bp.toLocaleString('en') + ' BP'; const t = document.createElement('span'); t.textContent = s.bp.toLocaleString('en'); d.append(t); bar.append(d); });
    const ticks = []; for (let v = 0; v <= max; v += 1000) ticks.push(v);
    axis.innerHTML = ticks.map((v, i) => '<span style="left:' + (v / max * 100).toFixed(1) + '%">' + (v === 0 ? 'Today' : v.toLocaleString('en') + (i === ticks.length - 1 ? ' years' : '')) + '</span>').join('');
  }

  /* ---------- form prefill: documents / products / species chosen on the page ---------- */
  const prefill = (o) => {
    const f = $('#form'); if (!f) return;
    const tick = (name, val) => { const el = $$('input[name=' + name + ']', f).find((i) => i.value === val); if (el) el.checked = true; };
    if (o.species) tick('species', o.species);
    (o.need || []).forEach((n) => tick('need', n));
    if (o.text) { const m = f.elements.message; m.value = (m.value ? m.value.replace(/\s*$/, '') + '\n' : '') + o.text; }
  };

  /* ---------- specification toolkit ---------- */
  function spec() {
    const S = window.BFF_SPEC; if (!S) return;
    const tabs = $('[data-spec-tabs]'), rows = $('[data-spec-rows]'), title = $('[data-spec-title]'), note = $('[data-spec-note]'), kind = $('[data-spec-kind]'), tbcNote = $('[data-spec-tbc]'), docs = $('[data-docs]');
    let cur = S.species[0].id;
    tabs.innerHTML = S.species.map((s) => '<button type="button" role="tab" id="tab-' + s.id + '" data-id="' + s.id + '" aria-selected="false" tabindex="-1">' + esc(s.name) + '</button>').join('');
    const render = (id, focus) => {
      cur = id; const s = S.species.find((x) => x.id === id);
      $$('button', tabs).forEach((b) => { const on = b.dataset.id === id; b.setAttribute('aria-selected', String(on)); b.tabIndex = on ? 0 : -1; if (on && focus) b.focus(); });
      kind.textContent = s.ancient ? 'Ancient wood · carbon-dated' : 'From the forest';
      title.textContent = s.name + ' multilayer board'; note.textContent = s.note || '';
      const list = S.rows.filter((r) => !r.only || (r.only === 'ancient') === !!s.ancient);
      rows.innerHTML = list.map((r) => '<div class="spec__row"><dt>' + esc(r.k) + '</dt><dd>' + esc(r.v.replace('{colour}', s.colour || '')) + (r.tbc && !S.confirmed ? ' <em class="tbc">TBC</em>' : '') + '</dd></div>').join('');
      tbcNote.hidden = S.confirmed || !list.some((r) => r.tbc);
      tabs.setAttribute('aria-label', 'Species'); $('.spec__card').setAttribute('aria-labelledby', 'tab-' + id);
    };
    tabs.addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) render(b.dataset.id); });
    tabs.addEventListener('keydown', (e) => {
      const k = { ArrowRight: 1, ArrowLeft: -1 }[e.key]; if (!k) return;
      const i = S.species.findIndex((s) => s.id === cur); render(S.species[(i + k + S.species.length) % S.species.length].id, true); e.preventDefault();
    });
    docs.innerHTML = S.docs.map((d) => '<li><button type="button" class="doc" data-doc="' + d.id + '"><span><b>' + esc(d.label) + '</b><em>' + esc(d.kind) + '</em></span><i aria-hidden="true">Request</i></button></li>').join('');
    docs.addEventListener('click', (e) => { const b = e.target.closest('[data-doc]'); if (!b) return; const d = S.docs.find((x) => x.id === b.dataset.doc); prefill({ need: ['documents'], text: 'Please send: ' + d.label + '.' }); go('#samples'); });
    // species discs choose the species and bring the reader to its specification
    $$('[data-species]').forEach((b) => b.addEventListener('click', () => { render(b.dataset.species); go('#specify'); }));
    // buttons that carry what they are about into the form
    $$('[data-prefill]').forEach((a) => a.addEventListener('click', () => {
      const k = a.dataset.prefill, o = { patterns: { need: ['patterns'] }, walls: { need: ['walls and ceilings'] }, stairs: { need: ['stairs'] }, tables: { need: ['tables and cellars'] }, spec: { species: cur.replace('-', ' '), text: 'Please send the ' + S.species.find((s) => s.id === cur).name + ' specification and samples.' } }[k];
      if (o) prefill(o);
    }));
    render(cur);
  }
  const go = (sel) => { const t = $(sel); if (!t) return; if (BFF.lenis) BFF.lenis.scrollTo(t, { offset: -70, duration: 1.4 }); else t.scrollIntoView({ behavior: BFF.reduce ? 'auto' : 'smooth' }); };

  BFF.fx.studio = { init() { accordion(); hotspots(); rings(); age(); spec(); } };
})();
