// The wood's journey as one 3D object: a bog trunk turns, shows its rings, opens, becomes boards
// and finally a floor. Textures are cut from the client's own photos (scripts/make_textures.py).
// Scroll drives one scalar t (0..6); each integer step is one beat between two chapters.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { gsap } from 'gsap';

const R = 0.78, LEN = 4.2;

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
  const [rings, disc, inside, bark, chevron] = await Promise.all([
    load('rings'), load('disc'), load('inside'),
    load('bark', { wrapS: THREE.RepeatWrapping, wrapT: THREE.RepeatWrapping }),
    load('chevron', { wrapS: THREE.RepeatWrapping, wrapT: THREE.RepeatWrapping })
  ]);
  bark?.repeat.set(5, 2.2);
  const boardTex = inside?.clone(); if (boardTex) { boardTex.needsUpdate = true; boardTex.rotation = Math.PI / 2; boardTex.center.set(0.5, 0.5); }

  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.82, metalness: 0, transparent: true, ...o });
  const barkMat = std({ map: bark, bumpMap: bark, bumpScale: 2.4, color: 0x453e37, roughness: 1 });
  const capMat = std({ map: rings, roughness: 0.8, color: 0xcbbfa9 });
  const insideMat = std({ map: inside, roughness: 0.7 });
  const mats = [barkMat, capMat, insideMat];

  // ---------- the trunk: two half-cylinders so one cut can open it ----------
  function half(thetaStart) {
    const g = new THREE.CylinderGeometry(R, R, LEN, 80, 28, false, thetaStart, Math.PI);
    const p = g.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i), y = p.getY(i), z = p.getZ(i), a = Math.atan2(x, z), r = Math.hypot(x, z);
      const n = 1 + 0.06 * Math.sin(a * 3 + y * 1.7) + 0.04 * Math.sin(a * 5 - y * 2.9 + 1.3) + 0.035 * Math.sin(y * 3.3);
      const taper = 1 + 0.07 * (y / LEN);
      const k = (1 + (n - 1) * (r / R)) * taper;
      p.setXYZ(i, x * k, y, z * k);
    }
    g.computeVertexNormals();
    return new THREE.Mesh(g, [barkMat, capMat, capMat]);
  }
  const faceGeo = new THREE.PlaneGeometry(2 * R * 0.98, LEN * 0.995);
  const top = new THREE.Group(), bottom = new THREE.Group();
  const topMesh = half(0), bottomMesh = half(Math.PI);
  const topFace = new THREE.Mesh(faceGeo.clone().rotateY(-Math.PI / 2), insideMat); topFace.position.x = 0.002;
  const botFace = new THREE.Mesh(faceGeo.clone().rotateY(Math.PI / 2), insideMat); botFace.position.x = -0.002;
  top.add(topMesh, topFace); bottom.add(bottomMesh, botFace);

  const spin = new THREE.Group(); spin.rotation.z = Math.PI / 2; spin.add(top, bottom);
  const roll = new THREE.Group(); roll.add(spin);
  const yaw = new THREE.Group(); yaw.add(roll); scene.add(yaw);

  // dated disc, seen on the cut end
  const discMat = std({ map: disc, roughness: 0.75, opacity: 0, depthWrite: false });
  const discMesh = new THREE.Mesh(new THREE.CircleGeometry(R * 0.93, 80), discMat);
  discMesh.rotation.y = -Math.PI / 2; discMesh.position.x = -LEN / 2 - 0.004; // faces the -X end
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
  const shadow = new THREE.Mesh(new THREE.PlaneGeometry(7.5, 3.2), shadowMat); shadow.rotation.x = -Math.PI / 2; shadow.position.y = -1.02; scene.add(shadow);

  // ---------- keyframes (t: 0..6, one unit per beat) ----------
  const P = { fade: 0, roll: 0, yaw: 0.55, scale: 0.6, camZ: 9.6, camY: 0.5, lookY: 0, split: 0, tilt: 0, topFade: 1, bottom: 1,
    boards: 0, spread: 0, lift: 0, pattern: 0, floor: 0, disc: 0, shadow: 0, topDown: 0, stack: 1 };
  const TAU = Math.PI * 2, tl = gsap.timeline({ paused: true, defaults: { ease: 'none' } });
  // beat 0: the trunk appears out of the dark and makes a full turn
  tl.to(P, { fade: 1, scale: 1, duration: 0.5 }, 0).to(P, { roll: TAU, yaw: 0.38, camZ: 8.4, duration: 1 }, 0).to(P, { shadow: 0.5, duration: 0.6 }, 0.2)
  // beat 1: the cut end turns to the camera; the dated disc fades in
    .to(P, { yaw: Math.PI / 2, camZ: 6.2, camY: 0.1, duration: 1 }, 1).to(P, { disc: 1, duration: 0.45 }, 1.5)
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
    yaw.rotation.y = P.yaw; roll.rotation.x = P.roll; yaw.scale.setScalar(P.scale * (1 - P.topDown * 0.0));
    yaw.visible = o > 0.001 && (P.bottom > 0.001 || P.topFade > 0.001 || P.disc > 0);
    spin.visible = P.bottom > 0.001 || P.topFade > 0.001;
    top.position.x = P.split; top.rotation.z = -P.tilt * 0.35; top.rotation.y = P.tilt * 0.18;
    top.visible = P.topFade > 0.01; bottom.visible = P.bottom > 0.01;
    setOpacity(barkMat, o * (P.bottom > P.topFade ? P.bottom : Math.max(P.topFade, P.bottom)));
    setOpacity(capMat, o * Math.max(P.topFade, P.bottom)); setOpacity(insideMat, o * Math.max(P.topFade, P.bottom));
    setOpacity(discMat, o * P.disc);
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
