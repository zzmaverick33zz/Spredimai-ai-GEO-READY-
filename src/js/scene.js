// The wood's journey as one 3D object: a bog trunk turns, shows its rings, opens, becomes boards
// and finally a floor. Textures are cut from the client's own photos (scripts/make_textures.py).
// Scroll drives one scalar t (0..6); each integer step is one beat between two chapters.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { gsap } from 'gsap';
import PROFILE from './trunk-profile.json';   // scanned from the reference trunk photo (scripts/scan_trunk.py)

const LEN = 4.8, R = LEN / PROFILE.lenOverR;

export async function createScene(canvas) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.setClearColor(0x000000, 0);

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.32;
  scene.fog = new THREE.FogExp2(0x081013, 0.0);

  const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 60);

  const key = new THREE.DirectionalLight(0xffe0b8, 2.6); key.position.set(3.5, 5, 5); scene.add(key);
  const rim = new THREE.DirectionalLight(0x7fb5b0, 0.95); rim.position.set(-5, 2, -4); scene.add(rim);
  scene.add(new THREE.HemisphereLight(0xcfe3e0, 0x24180e, 0.35));

  // ---------- textures ----------
  const loader = new THREE.TextureLoader();
  const load = (n, opts = {}) => new Promise(res => loader.load(window.__TEX__?.[n] ?? `/media/3d/${n}.webp`, t => {
    t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
    Object.assign(t, opts); res(t);
  }, undefined, () => res(null)));
  const [rings, disc, inside, bark, chevron, cutout] = await Promise.all([
    load('rings'), load('disc'), load('inside'),
    load('trunk-photo', { wrapS: THREE.ClampToEdgeWrapping, wrapT: THREE.ClampToEdgeWrapping }),
    load('chevron', { wrapS: THREE.RepeatWrapping, wrapT: THREE.RepeatWrapping }),
    load('trunk-cutout')
  ]);
  const boardTex = inside?.clone(); if (boardTex) { boardTex.needsUpdate = true; boardTex.rotation = Math.PI / 2; boardTex.center.set(0.5, 0.5); }

  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.82, metalness: 0, transparent: true, ...o });
  // the photo is projected onto the mesh, so it carries its own light; the 3D lights only add a little relief and sheen
  const barkMat = new THREE.MeshPhysicalMaterial({ map: bark, emissiveMap: bark, emissive: 0xffffff, emissiveIntensity: 0.72, bumpMap: bark, bumpScale: 4, color: 0x5e5e5e, roughness: 0.86, clearcoat: 0.04, clearcoatRoughness: 0.8, envMapIntensity: 0.12, transparent: true });
    const buttMat = std({ map: bark, color: 0x6e6254, roughness: 1, side: THREE.DoubleSide });   // the broken butt end: dark, muddy
  const capMat = std({ map: rings, roughness: 0.8, color: 0xcbbfa9 });
  const insideMat = std({ map: inside, roughness: 0.7 });
  
  // ---------- the trunk: two half-cylinders so one cut can open it ----------
  // Outline, centre line and ragged butt (u = 0) are scanned from the reference photo; the photo itself is projected on the mesh.
  const NB = PROFILE.yc.length, R0 = PROFILE.R0, TEXW = PROFILE.bbox[0], TEXH = PROFILE.bbox[1];
  const bin = (arr, u) => { const x = Math.min(Math.max(u * NB - 0.5, 0), NB - 1), i = Math.floor(x), j = Math.min(i + 1, NB - 1); return arr[i] + (arr[j] - arr[i]) * (x - i); };
  const sstep = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
  const kAt = (u) => { const k = bin(PROFILE.hh, Math.max(u, 0.1)) / R0; return k + (Math.max(0.92, k) - k) * 0.55 * sstep(0.4, 1, u); };   // photo radius, with the far taper eased (part of it is perspective)                                            // radius factor along the axis
  const shiftAt = (u) => (bin(PROFILE.yc, Math.max(u, 0.04)) - PROFILE.cy) / R0;                       // centre line, in radii (down is +)
  const wobble = (a, y) => 1 + 0.012 * Math.sin(a * 3 + y * 1.7) + 0.01 * Math.sin(a * 5 - y * 2.9 + 1.3);
  const retreat = (a) => {                                                                              // how far the butt rim sits back, per angle
    const n = Math.sin(a), row = bin(PROFILE.yc, 0.1) + n * bin(PROFILE.hh, 0.1) - PROFILE.rowsTop;
    const j = Math.min(PROFILE.end.length - 1, Math.max(0, row)), i = Math.floor(j), f = j - i;
    const e = PROFILE.end[i] + (PROFILE.end[Math.min(i + 1, PROFILE.end.length - 1)] - PROFILE.end[i]) * f;
    return Math.max(0, e) * LEN;
  };
  function shape(x, y, z, a, r) {                                                                       // r: 0 at axis, 1 at rim
    let ny = y; const u0 = (y + LEN / 2) / LEN;
    if (u0 < 0.12) ny += retreat(a) * Math.pow(sstep(0.12, 0, u0), 1.1) * (0.3 + 0.7 * r) + (1 - r) * 0.1 * sstep(0.12, 0, u0);
    const u = (ny + LEN / 2) / LEN, k = kAt(u) * (1 + (wobble(a, y) - 1) * r);
    return [x * k + shiftAt(u) * R, ny, z * k];                                                         // local x is "down" on screen
  }
  // Around the log the photo is used as in the picture for the visible front (|angle| < 50 deg), then the bark is
  // continued by mirroring, so turning the log never stretches the edge of the photo into streaks.
  const TH0 = 50 * Math.PI / 180, S0 = Math.sin(TH0), C0 = Math.cos(TH0), HI = 0.8, LO = 0.42;
  const around = (th) => {
    const sg = th < 0 ? -1 : 1, t = Math.abs(th);
    if (t <= TH0) return Math.sin(th);
    let m = S0 + C0 * (t - TH0);
    for (let i = 0; i < 12 && (m > HI || m < LO); i++) m = m > HI ? 2 * HI - m : 2 * LO - m;
    return sg * m;
  };
  const uvFor = (xPre, zPre, yFinal) => {                                                               // photo coordinates for a vertex
    const u = Math.min(1, Math.max(0, (yFinal + LEN / 2) / LEN)), n = around(Math.atan2(xPre, zPre));
    const px = PROFILE.x0 + u * PROFILE.len, py = bin(PROFILE.yc, u) + n * bin(PROFILE.hh, u);
    return [px / TEXW, 1 - py / TEXH];
  };
  function half(thetaStart) {
    const rs = 128, hs = 120, g = new THREE.CylinderGeometry(R, R, LEN, rs, hs, false, thetaStart, Math.PI);
    const p = g.attributes.position, uv = g.attributes.uv, torso = (rs + 1) * (hs + 1), cap = 2 * rs + 1;
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i), y = p.getY(i), z = p.getZ(i), a = Math.atan2(x, z), r = Math.min(1, Math.hypot(x, z) / R);
      const [nx, ny, nz] = shape(x, y, z, a, r); p.setXYZ(i, nx, ny, nz);
      if (i < torso) { const [uu, vv] = uvFor(x, z, ny); uv.setXY(i, uu, vv); }
      else if (i >= torso + cap) uv.setXY(i, 0.1 + 0.09 * (z / R), 0.5 + 0.2 * (x / R));      // butt end: a patch of muddy bark, not a stretched edge
    }
    g.computeVertexNormals();
    const nrm = g.attributes.normal;                                                                    // flat, even shading on both ends (no fan facets)
    for (let i = torso; i < p.count; i++) nrm.setXYZ(i, 0, i < torso + cap ? 1 : -1, 0);
    return new THREE.Mesh(g, [barkMat, capMat, buttMat]);
  }
  function face(rot) {                                                                                  // the cut surface follows the same outline
    const g = new THREE.PlaneGeometry(2 * R, LEN, 28, 96).rotateY(rot), p = g.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const y = p.getY(i), z = p.getZ(i), a = z >= 0 ? 0 : Math.PI, r = Math.min(1, Math.abs(z) / R);
      const [nx, ny, nz] = shape(0, y, z, a, r); p.setXYZ(i, nx, ny, nz);
    }
    g.computeVertexNormals(); return g;
  }
  // local +x is down on screen, so the half that goes up when the trunk opens is the x <= 0 one
  const upper = new THREE.Group(), lower = new THREE.Group();
  upper.add(half(Math.PI), new THREE.Mesh(face(Math.PI / 2), insideMat)); upper.children[1].position.x = -0.03;
  lower.add(half(0), new THREE.Mesh(face(-Math.PI / 2), insideMat)); lower.children[1].position.x = 0.03;

  const spin = new THREE.Group(); spin.rotation.z = -Math.PI / 2; spin.add(upper, lower);
  const roll = new THREE.Group(); roll.add(spin);
  const yaw = new THREE.Group(); yaw.add(roll); const hang = new THREE.Group(); hang.add(yaw); const turn = new THREE.Group(); turn.add(hang); scene.add(turn);   // turn: the turntable spin, hang: the tilt it hangs at

  // the reference photograph itself, as the first frame: same pose and outline as the mesh, then it fades into the 3D
  const photoMat = new THREE.MeshBasicMaterial({ map: cutout, transparent: true, opacity: 0, depthTest: false, depthWrite: false, toneMapped: false });
  const photo = new THREE.Mesh(new THREE.PlaneGeometry(TEXW / R0 * R, TEXH / R0 * R), photoMat);
  photo.position.set((TEXW / 2 - (PROFILE.x0 + PROFILE.len / 2)) / R0 * R, -(TEXH / 2 - PROFILE.cy) / R0 * R, 0.4); photo.renderOrder = 10; hang.add(photo);

  // dated disc, seen on the cut end
  const discMat = std({ map: disc, roughness: 0.75, opacity: 0, depthWrite: false });
  const discMesh = new THREE.Mesh(new THREE.CircleGeometry(R * kAt(1) * 0.97, 80), discMat);
  discMesh.rotation.y = Math.PI / 2; discMesh.position.set(LEN / 2 + 0.004, shiftAt(1) * -R, 0); // faces the +X end (the sawn top)
  yaw.add(discMesh);

  // ---------- boards (drying stack) ----------
  const boardMat = std({ map: boardTex, roughness: 0.7, color: 0xe0cdb2 });
  const stickMat = std({ color: 0x2a1f16, roughness: 0.9 });
  const boards = new THREE.Group(), BN = 6, TH = 0.11, BW = 1.45, BL = LEN * 0.96;
  const boardMeshes = [];
  for (let i = 0; i < BN; i++) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(BL, TH, BW), boardMat); m.userData.i = i; boards.add(m); boardMeshes.push(m);
  }
  const sticks = [];
  for (let i = 0; i < BN - 1; i++) for (const x of [-1.5, 0, 1.5]) {
    const s = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.05, BW), stickMat); s.userData = { i, x }; boards.add(s); sticks.push(s);
  }
  // pattern laid on the top board
  const patMat = std({ map: chevron, roughness: 0.55, opacity: 0, depthWrite: false, color: 0xffffff });
  chevron?.repeat.set(2, 1);
  const pattern = new THREE.Mesh(new THREE.PlaneGeometry(BL * 0.98, BW * 0.98), patMat);
  pattern.rotation.x = -Math.PI / 2; boards.add(pattern);
  scene.add(boards);

  // ---------- floor: herringbone of small boards ----------
  const FX = 11, FZ = 5, FN = FX * FZ * 3;
  const floorMat = std({ map: chevron, roughness: 0.55, color: 0xd6cbbb });
  const floorMesh = new THREE.InstancedMesh(new THREE.BoxGeometry(0.955, 0.04, 0.315), floorMat, FN);
  const dummy = new THREE.Object3D(), tint = new THREE.Color();
  const floorData = [];
  for (let i = 0; i < FX; i++) for (let j = 0; j < FZ; j++) for (let k = 0; k < 3; k++) {
    const idx = (i * FZ + j) * 3 + k, along = (i + j) % 2 === 0, off = (k - 1) * 0.32;
    const cx = (i - (FX - 1) / 2) * 0.96, cz = (j - (FZ - 1) / 2) * 0.96;
    floorData.push({ fx: cx + (along ? 0 : off), fz: cz + (along ? off : 0), ang: along ? 0 : Math.PI / 2, delay: Math.random() * 0.5, h: 2.5 + Math.random() * 2.2, sx: (Math.random() - 0.5) * 3, sz: (Math.random() - 0.5) * 3 });
    tint.setHSL(0.08 + Math.random() * 0.02, 0.1 + Math.random() * 0.1, 0.5 + Math.random() * 0.22); floorMesh.setColorAt(idx, tint);
  }
  floorMesh.instanceColor.needsUpdate = true;
  floorMesh.visible = false; scene.add(floorMesh);
  const underMat = std({ color: 0x2b2118, roughness: 1, opacity: 0, depthWrite: false });
  const under = new THREE.Mesh(new THREE.PlaneGeometry(FX * 0.96, FZ * 0.96), underMat); under.rotation.x = -Math.PI / 2; under.position.y = -1.025; under.visible = false; scene.add(under);

  // soft contact shadow
  const sc = document.createElement('canvas'); sc.width = sc.height = 128;
  const sx = sc.getContext('2d'), gr = sx.createRadialGradient(64, 64, 4, 64, 64, 64);
  gr.addColorStop(0, 'rgba(0,0,0,.55)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); sx.fillStyle = gr; sx.fillRect(0, 0, 128, 128);
  const shadowMat = new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(sc), transparent: true, depthWrite: false, opacity: 0 });
  const shadow = new THREE.Mesh(new THREE.PlaneGeometry(7.5, 3.2), shadowMat); shadow.rotation.x = -Math.PI / 2; shadow.position.y = -1.05; scene.add(shadow);

  // ---------- keyframes (t: 0..6, one unit per beat) ----------
  const P = { photo: 1, turn: 0, hang: 0.395, fade: 0, roll: 0, yaw: 0, scale: 0.6, camZ: 9.6, camY: 0.5, lookY: 0, split: 0, tilt: 0, topFade: 1, bottom: 1,
    boards: 0, spread: 0, lift: 0, pattern: 0, floor: 0, disc: 0, shadow: 0, topDown: 0, stack: 1 };
  const TAU = Math.PI * 2, tl = gsap.timeline({ paused: true, defaults: { ease: 'none' } });
  // beat 0: the trunk appears out of the dark and makes a full turn
  tl.to(P, { fade: 1, scale: 1, duration: 0.4 }, 0).to(P, { camZ: 9.4, duration: 0.45 }, 0).to(P, { photo: 0, duration: 0.18 }, 0.34).to(P, { turn: -TAU, hang: 0, yaw: 0.1, duration: 0.6 }, 0.4).to(P, { shadow: 0.5, duration: 0.6 }, 0.4)
  // beat 1: the cut end turns to the camera; the dated disc fades in
    .to(P, { yaw: -Math.PI / 2, camZ: 6.4, camY: 0.1, duration: 1 }, 1).to(P, { disc: 1, duration: 0.45 }, 1.5)
  // beat 2: back to the side, one cut opens the trunk
    .to(P, { disc: 0, duration: 0.2 }, 2).to(P, { yaw: 0.2, camZ: 9.4, camY: 3.4, lookY: -0.45, duration: 1 }, 2)
    .to(P, { split: 1.15, tilt: 0.42, duration: 0.8 }, 2.2)
  // beat 3: halves part, the lower one becomes a drying stack
    .to(P, { split: 2.6, tilt: 0.9, topFade: 0, duration: 0.4 }, 3)
    .to(P, { bottom: 0, boards: 1, duration: 0.25 }, 3.15).to(P, { spread: 1, camZ: 8.4, camY: 2.4, lookY: -0.1, duration: 0.8 }, 3.25)
  // beat 4: one board is lifted and takes a pattern
    .to(P, { lift: 1, camZ: 7.0, camY: 1.6, lookY: 0.3, yaw: 0.35, duration: 0.8 }, 4).to(P, { pattern: 1, duration: 0.5 }, 4.45)
  // beat 5: boards part, a herringbone floor lays itself, camera looks down
    .to(P, { stack: 0, duration: 0.35 }, 5).to(P, { floor: 1, duration: 0.8 }, 5.15)
    .to(P, { topDown: 1, camY: 9, camZ: 0.35, lookY: 0, yaw: 0, shadow: 0, duration: 1 }, 5);
  tl.duration(6);

  // ---------- apply state ----------
  const ease = (x) => x * x * (3 - 2 * x);
  const mouse = { x: 0, y: 0, tx: 0, ty: 0 };
  addEventListener('pointermove', (e) => { mouse.tx = e.clientX / innerWidth - 0.5; mouse.ty = e.clientY / innerHeight - 0.5; }, { passive: true });
  const setOpacity = (m, o) => { m.opacity = o; m.depthWrite = o > 0.98; };
  const fogColor = new THREE.Color();

  function apply() {
    const o = P.fade;
    yaw.rotation.y = P.yaw; roll.rotation.x = P.roll; hang.rotation.z = -P.hang; turn.rotation.y = P.turn; yaw.scale.setScalar(P.scale * (1 - P.topDown * 0.0));
    yaw.visible = o > 0.001 && (P.bottom > 0.001 || P.topFade > 0.001 || P.disc > 0);
    turn.visible = yaw.visible;
    spin.visible = P.bottom > 0.001 || P.topFade > 0.001;
    upper.position.x = -P.split; upper.rotation.z = P.tilt * 0.35; upper.rotation.y = P.tilt * 0.18;
    upper.visible = P.topFade > 0.01; lower.visible = P.bottom > 0.01;
    upper.children[1].visible = lower.children[1].visible = P.split > 0.03;     // the cut faces only exist once the trunk is opened
    setOpacity(barkMat, o * (P.bottom > P.topFade ? P.bottom : Math.max(P.topFade, P.bottom)));
    setOpacity(capMat, o * Math.max(P.topFade, P.bottom)); setOpacity(insideMat, o * Math.max(P.topFade, P.bottom));
    setOpacity(discMat, o * P.disc);
    photo.visible = P.photo > 0.003; photoMat.opacity = o * P.photo;
    // boards
    boards.visible = P.boards > 0.01 && P.stack > 0.01;
    const sp = ease(P.spread), lf = ease(P.lift);
    boardMeshes.forEach((m, i) => {
      const gap = 0.012 + sp * 0.115, y = -0.42 + i * (TH + gap) - (BN * (TH + gap)) / 2 + 0.42 + (sp > 0 ? -0.25 : 0);
      m.position.set(0, y + (i === BN - 1 ? lf * 0.95 : 0), i === BN - 1 ? lf * 0.35 : 0);
      m.rotation.set(i === BN - 1 ? lf * 0.75 : 0, 0, 0);
      m.scale.setScalar(1);
    });
    sticks.forEach((s) => {
      const gap = 0.012 + sp * 0.115, i = s.userData.i;
      s.position.set(s.userData.x, -0.42 + i * (TH + gap) - (BN * (TH + gap)) / 2 + 0.42 + (sp > 0 ? -0.25 : 0) + (TH + gap) / 2, 0);
      s.visible = sp > 0.15 && !(i === BN - 2 && lf > 0.05);
    });
    const tb = boardMeshes[BN - 1], rx = tb.rotation.x;
    pattern.position.set(0, tb.position.y + (TH / 2 + 0.004) * Math.cos(rx), tb.position.z + (TH / 2 + 0.004) * Math.sin(rx));
    pattern.rotation.set(rx - Math.PI / 2, 0, 0);
    pattern.visible = P.pattern > 0.01;
    setOpacity(patMat, P.pattern * (1 - P.floor));
    const bo = o * P.boards * P.stack; setOpacity(boardMat, bo); setOpacity(stickMat, bo);
    boards.position.y = 0; boards.rotation.y = P.yaw * 0.6;
    // floor
    floorMesh.visible = P.floor > 0.001; under.visible = floorMesh.visible && P.floor > 0.7;
    if (floorMesh.visible) {
      for (let i = 0; i < FN; i++) {
        const d = floorData[i], k = ease(Math.min(1, Math.max(0, (P.floor - d.delay * 0.45) / 0.55)));
        dummy.position.set(d.fx + d.sx * (1 - k), -1.0 + (1 - k) * d.h, d.fz + d.sz * (1 - k));
        dummy.rotation.set((1 - k) * 2.2, d.ang + (1 - k) * 1.5, (1 - k) * 0.8); dummy.scale.setScalar(0.3 + 0.7 * k);
        dummy.updateMatrix(); floorMesh.setMatrixAt(i, dummy.matrix);
      }
      floorMesh.instanceMatrix.needsUpdate = true; setOpacity(floorMat, Math.min(1, P.floor * 3)); under.visible = true; setOpacity(underMat, Math.max(0, (P.floor - 0.7) / 0.3));
    }
    shadowMat.opacity = P.shadow * o * Math.max(P.bottom, P.boards * P.stack > 0.2 ? 0.6 : 0);
    shadow.visible = shadowMat.opacity > 0.01;
    // camera
    const w = canvas.clientWidth || innerWidth, h = canvas.clientHeight || innerHeight, asp = w / h;
    const fit = asp < 1.35 ? Math.pow(1.35 / asp, 0.8) : 1;
    const portrait = asp < 1;
    floorMesh.rotation.y = portrait ? Math.PI / 2 : 0; under.rotation.z = portrait ? Math.PI / 2 : 0;
    mouse.x += (mouse.tx - mouse.x) * 0.05; mouse.y += (mouse.ty - mouse.y) * 0.05;
    camera.position.set(mouse.x * 0.8 * (1 - P.topDown), P.camY * fit + mouse.y * 0.4, P.camZ * (P.topDown > 0.5 ? 1 : fit));
    camera.lookAt(0, P.lookY, 0);
    // fog follows the page ground so the trunk melts into it
    const bg = getComputedStyle(document.body).backgroundColor.match(/\d+/g);
    if (bg) { fogColor.setRGB(bg[0] / 255, bg[1] / 255, bg[2] / 255, THREE.SRGBColorSpace); scene.fog.color.copy(fogColor); }
    scene.fog.density = 0.028 * (1 - o) + 0.012 * (1 - P.topDown);
  }

  function size() {
    const w = innerWidth, h = innerHeight;
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  addEventListener('resize', size); size();

  let t = 0, target = 0, live = false, raf = 0;
  function frame() {
    raf = 0; if (!live) return;
    t += (target - t) * 0.12; if (Math.abs(target - t) < 0.0005) t = target;
    tl.time(Math.min(6, Math.max(0, t))); apply(); renderer.render(scene, camera);
    raf = requestAnimationFrame(frame);
  }
  return {
    setT(v) { target = v; },
    jumpT(v) { target = t = v; tl.time(v); apply(); renderer.render(scene, camera); },
    setLive(v) { live = v; if (v && !raf) raf = requestAnimationFrame(frame); },
    renderer
  };
}
