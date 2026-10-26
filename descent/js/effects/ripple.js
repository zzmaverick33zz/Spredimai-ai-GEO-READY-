/* Effect 1: water ripple on the hero (and, weaker, chapter I).
   Behaviour modelled on 21st.dev "Ripple Distortion" (ruixen.ui; params frequency, amplitude, speed): concentric ripples
   radiate from the cursor over the image. The component source needs a 21st.dev API key and could not be read, so this is
   written from its documented behaviour with raw WebGL (no three.js needed for one textured plane).
   Options (data- attributes on the .slot): data-ripple-frequency (14), data-ripple-amplitude (0.012), data-ripple-speed (0.6).
   Fallbacks: reduced motion, coarse pointer, no WebGL, or an image the browser will not give to WebGL -> plain <img>. */
(function () {
  'use strict';
  const { $$, reduce, clamp } = BFF;
  const N = 8;                                            // ripples alive at once
  const VS = 'attribute vec2 p;varying vec2 v;void main(){v=p*.5+.5;gl_Position=vec4(p,0.,1.);}';
  const FS = `precision mediump float;
varying vec2 v;uniform sampler2D tex;uniform vec2 res,img;uniform float t,freq,amp,speed;uniform vec4 r[${N}];
void main(){
  float ca=res.x/res.y, ia=img.x/img.y;
  vec2 s=ca>ia?vec2(1.,ia/ca):vec2(ca/ia,1.);        // object-fit: cover
  vec2 off=amp*.35*vec2(sin(v.y*6.+t*.35),cos(v.x*5.+t*.3));   // slow idle swell
  for(int i=0;i<${N};i++){
    vec4 q=r[i]; float age=t-q.z;
    if(q.w>0.&&age>0.){
      vec2 d=(v-q.xy)*vec2(ca,1.); float dist=length(d), front=age*speed;
      float env=max(0.,1.-age/1.5)*exp(-dist*2.2)*smoothstep(front+.06,front-.14,dist);
      off+=normalize(d+1e-5)*sin((dist-front)*freq*6.2832)*env*amp*q.w;
    }
  }
  vec2 uv=(v+off-.5)*s+.5; gl_FragColor=texture2D(tex,vec2(uv.x,1.-uv.y));
}`;

  function setup(slot) {
    const img = slot.querySelector('img');
    if (!img) return;
    const num = (a, d) => { const x = parseFloat(slot.getAttribute(a)); return isNaN(x) ? d : x; };
    const freq = num('data-ripple-frequency', 14), amp = num('data-ripple-amplitude', 0.012), speed = num('data-ripple-speed', 0.6);
    const canvas = document.createElement('canvas'); canvas.className = 'fx-ripple'; canvas.setAttribute('aria-hidden', 'true');
    const gl = canvas.getContext('webgl', { alpha: false, antialias: false, powerPreference: 'low-power' });
    if (!gl) return;
    const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)); return s; };
    const prog = gl.createProgram(); gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(prog); gl.useProgram(prog);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer()); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(prog, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    const U = (n) => gl.getUniformLocation(prog, n);
    const u = { tex: U('tex'), res: U('res'), img: U('img'), t: U('t'), freq: U('freq'), amp: U('amp'), speed: U('speed'), r: U('r') };
    const tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    // limit texture size so a big source never costs memory on weak GPUs
    const cap = Math.min(2048, gl.getParameter(gl.MAX_TEXTURE_SIZE));
    const upload = () => {
      let src = img;
      if (Math.max(img.naturalWidth, img.naturalHeight) > cap) {
        const k = cap / Math.max(img.naturalWidth, img.naturalHeight), c = document.createElement('canvas');
        c.width = Math.round(img.naturalWidth * k); c.height = Math.round(img.naturalHeight * k); c.getContext('2d').drawImage(img, 0, 0, c.width, c.height); src = c;
      }
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, src);   // throws SecurityError for cross-origin images (e.g. file://)
      gl.uniform2f(u.img, img.naturalWidth, img.naturalHeight);
    };
    const ripples = new Float32Array(N * 4); let head = 0, last = { x: -1e3, y: -1e3, t: 0 };
    const t0 = performance.now(), now = () => (performance.now() - t0) / 1000;
    const size = () => {
      const d = Math.min(devicePixelRatio || 1, 1.5), r = slot.getBoundingClientRect();
      canvas.width = Math.max(2, Math.round(r.width * d)); canvas.height = Math.max(2, Math.round(r.height * d)); gl.viewport(0, 0, canvas.width, canvas.height);
    };
    let raf = 0, on = false, ready = false;
    const frame = () => {
      raf = 0; if (!on) return;
      gl.uniform2f(u.res, canvas.width, canvas.height); gl.uniform1f(u.t, now()); gl.uniform4fv(u.r, ripples);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
      if (!ready) { ready = true; canvas.classList.add('is-ready'); }
      raf = requestAnimationFrame(frame);
    };
    const start = () => { try { upload(); } catch (e) { console.info('[ripple] texture not available, keeping the plain image:', e.name); canvas.remove(); return false; }
      gl.uniform1i(u.tex, 0); gl.uniform1f(u.freq, freq); gl.uniform1f(u.amp, amp); gl.uniform1f(u.speed, speed);
      slot.append(canvas); size(); new ResizeObserver(size).observe(slot);
      // the section (not only the slot) listens, so the headline layer above the image does not block the pointer
      const host = slot.closest('.hero, .chapter') || slot;
      host.addEventListener('pointermove', (e) => {
        if (e.pointerType === 'touch') return;
        const r = slot.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top;
        if (x < 0 || y < 0 || x > r.width || y > r.height) return;
        const tt = now(); if (Math.hypot(x - last.x, y - last.y) < 36 && tt - last.t < 0.35) return;
        last = { x, y, t: tt };
        ripples.set([clamp(x / r.width, 0, 1), clamp(1 - y / r.height, 0, 1), tt, 1], head * 4); head = (head + 1) % N;
      }, { passive: true });
      BFF.whenVisible(slot, () => { on = true; if (!raf) raf = requestAnimationFrame(frame); }, () => { on = false; });
      return true; };
    if (img.complete && img.naturalWidth) start(); else img.addEventListener('load', start, { once: true });
  }

  BFF.fx.ripple = {
    init() {
      if (reduce || BFF.coarse) return;
      $$('[data-ripple]').forEach((slot) => { try { setup(slot); } catch (e) { console.warn('[ripple]', e); } });
    }
  };
})();
