// Replaces a slot's placeholder with real media listed in public/media/manifest.json.
// Slots absent from the manifest keep their placeholder + brief.
export async function hydrateMedia() {
  let manifest = window.__MANIFEST__ || {};
  if (!window.__MANIFEST__) try {
    const r = await fetch('/media/manifest.json', { cache: 'no-cache' });
    if (r.ok) manifest = await r.json();
  } catch { /* no manifest yet */ }

  const reduce = new URLSearchParams(location.search).has('static') || matchMedia('(prefers-reduced-motion: reduce)').matches;
  for (const [id, m] of Object.entries(manifest)) {
    if (id.startsWith('_')) continue;
    const slot = document.querySelector(`[data-slot="${id}"]`);
    if (!slot || slot.hasAttribute('data-static')) continue;
    let el;
    if (m.type === 'video') {
      el = document.createElement('video');
      el.muted = true; el.loop = true; el.playsInline = true; el.preload = 'none';
      el.setAttribute('aria-hidden', 'true');
      el.poster = (m.posterMobile && matchMedia('(max-width: 899px)').matches) ? m.posterMobile : m.poster;
      for (const s of m.sources || []) {
        const so = document.createElement('source');
        so.src = s.src; so.type = s.type; if (s.media) so.media = s.media;
        el.append(so);
      }
    } else if (m.type === 'image') {
      el = document.createElement('picture');
      for (const s of m.sources || []) {
        const so = document.createElement('source');
        so.srcset = s.srcset; so.type = s.type; if (s.sizes) so.sizes = s.sizes;
        el.append(so);
      }
      const img = document.createElement('img');
      img.src = m.src; img.alt = m.alt || ''; img.loading = 'lazy'; img.decoding = 'async';
      if (m.width) img.width = m.width; if (m.height) img.height = m.height;
      el.append(img);
    } else continue;
    slot.querySelector('.slot__empty')?.remove();
    slot.prepend(el);
    if (m.illustration) {
      slot.dataset.illustration = 'true';
      const tag = document.createElement('span');
      tag.className = 'slot__tag';
      tag.textContent = 'Illustration';
      slot.append(tag);
    }
  }
}
