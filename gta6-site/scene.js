/* 3D neon city + drivable car – original artwork (not from any game) */
(function(){
  const canvas = document.getElementById("bg");
  window.SCENE = { boost(){}, ready:false };
  if (!canvas) return;
  let renderer;
  try {
    if (!window.THREE) throw new Error("no three");
    renderer = new THREE.WebGLRenderer({canvas, antialias:true, powerPreference:"high-performance"});
  } catch(e) { document.body.classList.add("no-webgl"); return; }

  const reduce = (()=>{try{return localStorage.getItem("motionOff")==="1"}catch(e){return false}})(); // motion is on unless the visitor turns it off with the 🎬 button
  const mobile = matchMedia("(max-width:720px)").matches;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, mobile ? 1.5 : 1.75));
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x12061f);
  scene.fog = new THREE.Fog(0x1a0830, 60, 260);
  const camera = new THREE.PerspectiveCamera(62, 1, 0.1, 500);

  scene.add(new THREE.HemisphereLight(0xff9ad5, 0x1a0830, 0.9));
  const sunLight = new THREE.DirectionalLight(0xffb36b, 1.1); sunLight.position.set(0, 20, -60); scene.add(sunLight);
  const rim = new THREE.DirectionalLight(0x29f0ff, 0.7); rim.position.set(-10, 6, 30); scene.add(rim);

  /* sky */
  scene.add(new THREE.Mesh(new THREE.SphereGeometry(400, 32, 16), new THREE.ShaderMaterial({
    side:THREE.BackSide, depthWrite:false, fog:false,
    vertexShader:"varying vec3 p; void main(){ p=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}",
    fragmentShader:"varying vec3 p; void main(){ float h=clamp(p.y*1.6+0.08,0.0,1.0); vec3 c=mix(vec3(1.0,0.38,0.45),vec3(0.42,0.10,0.45),smoothstep(0.0,0.35,h)); c=mix(c,vec3(0.07,0.02,0.14),smoothstep(0.35,1.0,h)); gl_FragColor=vec4(c,1.0);}"
  })));

  /* sun */
  const sunMat = new THREE.ShaderMaterial({
    transparent:true, fog:false, depthWrite:false, uniforms:{t:{value:0}},
    vertexShader:"varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}",
    fragmentShader:"uniform float t; varying vec2 vUv; void main(){ float d=distance(vUv,vec2(0.5)); if(d>0.5) discard; float y=vUv.y; if(y<0.55){ float s=sin(y*70.0-t*1.5); float th=mix(1.0,-0.5,(0.55-y)/0.55); if(s>th) discard; } vec3 c=mix(vec3(1.0,0.22,0.6),vec3(1.0,0.86,0.35),smoothstep(0.1,0.95,y)); gl_FragColor=vec4(c,smoothstep(0.5,0.38,d));}"
  });
  const sun = new THREE.Mesh(new THREE.PlaneGeometry(110,110), sunMat); sun.position.set(0,32,-300); scene.add(sun);

  /* stars */
  const sg = new THREE.BufferGeometry(); const sp = [];
  for (let i=0;i<500;i++){ const a=Math.random()*Math.PI*2, r=300+Math.random()*60; sp.push(Math.cos(a)*r, 60+Math.random()*200, -Math.abs(Math.sin(a)*r)); }
  sg.setAttribute("position", new THREE.Float32BufferAttribute(sp,3));
  scene.add(new THREE.Points(sg, new THREE.PointsMaterial({color:0xffffff,size:1.2,sizeAttenuation:false,transparent:true,opacity:.7,fog:false})));

  /* grid floor + road */
  const gridMat = new THREE.ShaderMaterial({
    fog:false, uniforms:{t:{value:0}}, extensions:{derivatives:true},
    vertexShader:"varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}",
    fragmentShader:"uniform float t; varying vec2 vUv; void main(){ vec2 g=vec2(vUv.x*90.0, vUv.y*90.0+t); vec2 f=abs(fract(g-0.5)-0.5)/fwidth(g); float l=1.0-min(min(f.x,f.y),1.0); float road=1.0-smoothstep(0.03,0.04,abs(vUv.x-0.5)); float dash=step(0.5,fract(vUv.y*45.0+t*0.5))*(1.0-smoothstep(0.0012,0.0022,abs(vUv.x-0.5))); vec3 col=mix(vec3(1.0,0.25,0.65),vec3(0.16,0.94,1.0),road); float fade=smoothstep(0.0,0.75,vUv.y); vec3 base=vec3(0.06,0.01,0.10)+road*vec3(0.05,0.03,0.08); gl_FragColor=vec4(base+col*l*0.9*fade*(1.0-road*0.6)+vec3(1.0,0.85,0.4)*dash*fade, 1.0);}"
  });
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(400,400), gridMat); floor.rotation.x=-Math.PI/2; floor.position.z=-170; scene.add(floor);

  /* buildings */
  const wc = document.createElement("canvas"); wc.width=64; wc.height=128; const x = wc.getContext("2d");
  x.fillStyle="#0b0516"; x.fillRect(0,0,64,128);
  const lit=["#ffd27a","#ff5fb0","#5ff3ff","#b38bff"];
  for (let r=0;r<16;r++) for (let c=0;c<6;c++) if (Math.random()<.42){ x.fillStyle=lit[(Math.random()*4)|0]; x.globalAlpha=.55+Math.random()*.45; x.fillRect(4+c*10,4+r*8,6,4); }
  const winTex = new THREE.CanvasTexture(wc);
  const N = mobile?70:130, LEN=340;
  const buildings = new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1), new THREE.MeshBasicMaterial({map:winTex}), N);
  const glows = new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1), new THREE.MeshBasicMaterial({color:0xff3fa4}), N);
  const bData=[]; const m4=new THREE.Matrix4(), q=new THREE.Quaternion(), sc=new THREE.Vector3(), ps=new THREE.Vector3();
  const tints=[0xffffff,0xffc6e6,0xc9f7ff,0xe0d0ff];
  for (let i=0;i<N;i++){ const side=i%2?1:-1; bData.push({x:side*(32+Math.random()*38), z:-LEN+Math.random()*(LEN+40), w:4+Math.random()*8, h:6+Math.pow(Math.random(),1.6)*48, d:4+Math.random()*8}); buildings.setColorAt(i,new THREE.Color(tints[i%4])); }
  scene.add(buildings); scene.add(glows);

  /* palms */
  const palms=[]; const dark=new THREE.MeshBasicMaterial({color:0x0a0312});
  const leafGeo=new THREE.ConeGeometry(.5,6,4); leafGeo.translate(0,3,0);
  const P=mobile?12:20;
  for (let i=0;i<P;i++){
    const g=new THREE.Group();
    const trunk=new THREE.Mesh(new THREE.CylinderGeometry(.18,.32,11,6),dark); trunk.position.y=5.5; trunk.rotation.z=(Math.random()-.5)*.25; g.add(trunk);
    const crown=new THREE.Group(); crown.position.y=11;
    for (let k=0;k<7;k++){ const leaf=new THREE.Mesh(leafGeo,dark); leaf.rotation.set(0,k/7*Math.PI*2,1.15+Math.random()*.4); leaf.scale.set(1,1,.35); crown.add(leaf); }
    g.add(crown); g.position.set((i%2?1:-1)*9.5,0,-LEN+(i/P)*(LEN+40)); g.userData={sway:Math.random()*6,crown}; scene.add(g); palms.push(g);
  }

  /* traffic light trails */
  const TR=mobile?60:120, tg=new THREE.BufferGeometry(), tp=new Float32Array(TR*3), tc=new Float32Array(TR*3), tv=[];
  for (let i=0;i<TR;i++){ const oncoming=i%2; tp[i*3]=oncoming?-3-Math.random()*1.5:3+Math.random()*1.5; tp[i*3+1]=.4; tp[i*3+2]=-LEN+Math.random()*(LEN+40); const c=new THREE.Color(oncoming?0xfff1c9:0xff3355); tc.set([c.r,c.g,c.b],i*3); tv.push(oncoming?50+Math.random()*30:-(30+Math.random()*30)); }
  tg.setAttribute("position",new THREE.BufferAttribute(tp,3)); tg.setAttribute("color",new THREE.BufferAttribute(tc,3));
  scene.add(new THREE.Points(tg,new THREE.PointsMaterial({size:mobile?3:4,sizeAttenuation:false,vertexColors:true,transparent:true,opacity:.95,blending:THREE.AdditiveBlending,depthWrite:false})));

  /* ---------- original low-poly sports car ---------- */
  const car = new THREE.Group();
  const paint = new THREE.MeshStandardMaterial({color:0xff2d95, metalness:.35, roughness:.3, emissive:0x3a0020});
  const black = new THREE.MeshStandardMaterial({color:0x120a1c, metalness:.2, roughness:.6});
  const glass = new THREE.MeshStandardMaterial({color:0x1d6a8a, metalness:.6, roughness:.1, emissive:0x06202c});
  const white = new THREE.MeshBasicMaterial({color:0xffffff});
  const red = new THREE.MeshBasicMaterial({color:0xff1f3d});
  const cyan = new THREE.MeshBasicMaterial({color:0x29f0ff});
  const add = (geo, mat, px, py, pz, rx) => { const m=new THREE.Mesh(geo,mat); m.position.set(px,py,pz); if (rx) m.rotation.x=rx; car.add(m); return m; };
  add(new THREE.BoxGeometry(2.2,.5,4.6), paint, 0,.6,0);                 // body
  add(new THREE.BoxGeometry(2.1,.28,1.3), paint, 0,.5,-2.6);              // nose
  add(new THREE.BoxGeometry(1.7,.5,1.9), black, 0,1.08,.25);              // cabin
  add(new THREE.BoxGeometry(1.6,.05,1.0), glass, 0,1.12,-.95, -0.75);     // windshield
  add(new THREE.BoxGeometry(1.6,.05,.8), glass, 0,1.1,1.35, 0.8);         // rear glass
  add(new THREE.BoxGeometry(.28,.02,6), white, 0,.87,-.3);                // stripe
  add(new THREE.BoxGeometry(2.3,.08,.45), black, 0,1.15,2.15);            // spoiler
  add(new THREE.BoxGeometry(.08,.3,.2), black, -.8,.98,2.15); add(new THREE.BoxGeometry(.08,.3,.2), black, .8,.98,2.15);
  add(new THREE.BoxGeometry(.55,.12,.05), white, -.7,.62,-3.26); add(new THREE.BoxGeometry(.55,.12,.05), white, .7,.62,-3.26); // headlights
  add(new THREE.BoxGeometry(1.9,.1,.05), red, 0,.72,2.31);                // tail light bar
  const wheels=[];
  const wGeo=new THREE.CylinderGeometry(.42,.42,.36,18); wGeo.rotateZ(Math.PI/2);
  const rGeo=new THREE.CylinderGeometry(.22,.22,.38,10); rGeo.rotateZ(Math.PI/2);
  [[-1.08,-1.5],[1.08,-1.5],[-1.08,1.5],[1.08,1.5]].forEach(([wx,wz])=>{ const w=new THREE.Group(); w.add(new THREE.Mesh(wGeo,black)); w.add(new THREE.Mesh(rGeo,cyan)); w.position.set(wx,.42,wz); car.add(w); wheels.push(w); });
  const under = new THREE.Mesh(new THREE.PlaneGeometry(3,5.4), new THREE.MeshBasicMaterial({color:0x29f0ff,transparent:true,opacity:.35,blending:THREE.AdditiveBlending,depthWrite:false}));
  under.rotation.x=-Math.PI/2; under.position.y=.04; car.add(under);
  const flame = new THREE.Mesh(new THREE.ConeGeometry(.25,1.6,8), new THREE.MeshBasicMaterial({color:0x6cf6ff,transparent:true,opacity:0,blending:THREE.AdditiveBlending,depthWrite:false}));
  flame.rotation.x=Math.PI/2; flame.position.set(0,.5,3.2); car.add(flame);
  car.position.set(0,0,12);
  scene.add(car);

  /* soft contact shadow (blob) under cars: cheap and grounds them in the scene */
  const shc=document.createElement("canvas"); shc.width=shc.height=128; const sx=shc.getContext("2d");
  const sgr=sx.createRadialGradient(64,64,6,64,64,62); sgr.addColorStop(0,"rgba(0,0,0,.85)"); sgr.addColorStop(.55,"rgba(0,0,0,.45)"); sgr.addColorStop(1,"rgba(0,0,0,0)");
  sx.fillStyle=sgr; sx.fillRect(0,0,128,128);
  const shadowMat=new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(shc),transparent:true,depthWrite:false});
  const addShadow=(g,w,l)=>{ const m=new THREE.Mesh(new THREE.PlaneGeometry(w,l),shadowMat); m.rotation.x=-Math.PI/2; m.position.y=.03; m.renderOrder=-1; m.userData.keep=true; g.add(m); return m; };
  addShadow(car,3.4,6.2);

  /* ---------- mini-game: traffic + cash ---------- */
  const G = { on:false, lane:0, score:0, coins:0, near:0, speed:30, over:false, cb:()=>{} };
  const LANES=[-3.6,0,3.6];
  const traffic=[], coins=[];
  const tColors=[0x29f0ff,0xffd23f,0x9b5cff,0x3dff8a,0xff7a29];
  for (let i=0;i<7;i++){
    const g=new THREE.Group();
    const bm=new THREE.MeshStandardMaterial({color:tColors[i%5],metalness:.3,roughness:.35,emissive:tColors[i%5],emissiveIntensity:.15});
    const b=new THREE.Mesh(new THREE.BoxGeometry(2.1,.7,4.2),bm); b.position.y=.7; g.add(b);
    const c=new THREE.Mesh(new THREE.BoxGeometry(1.7,.55,2),black); c.position.set(0,1.3,.2); g.add(c);
    const tl=new THREE.Mesh(new THREE.BoxGeometry(1.9,.14,.05),red); tl.position.set(0,.8,2.12); g.add(tl);
    [[-1,-1.4],[1,-1.4],[-1,1.4],[1,1.4]].forEach(([wx,wz])=>{ const w=new THREE.Mesh(wGeo,black); w.position.set(wx,.42,wz); g.add(w); });
    addShadow(g,3.2,5.8);
    g.visible=false; g.userData={v:0}; scene.add(g); traffic.push(g);
  }
  const coinGeo=new THREE.CylinderGeometry(.7,.7,.15,20); coinGeo.rotateX(Math.PI/2);
  const coinMat=new THREE.MeshBasicMaterial({color:0x3dff8a});
  for (let i=0;i<8;i++){ const m=new THREE.Mesh(coinGeo,coinMat); m.visible=false; scene.add(m); coins.push(m); }
  const pick=a=>a[(Math.random()*a.length)|0];

  /* ---------- real 3D models (Kenney, CC0) – loaded on top, boxes stay as fallback ---------- */
  const landmarks=[]; let carWheels=[];
  function glowUp(root, k){ root.traverse(o=>{ if (o.isMesh && o.material){ const m=o.material=o.material.clone(); if (m.map){ m.emissive=new THREE.Color(0xffffff); m.emissiveMap=m.map; m.emissiveIntensity=k; } } }); }
  function fitTo(obj, len, axis){ const b=new THREE.Box3().setFromObject(obj), s=new THREE.Vector3(); b.getSize(s); const f=len/(axis==="y"?s.y:s.z); obj.scale.setScalar(f); const b2=new THREE.Box3().setFromObject(obj); obj.position.y-=b2.min.y; return obj; }
  function loadModels(){
    const L=new THREE.GLTFLoader(), get=u=>new Promise((ok,no)=>L.load(u,g=>ok(g.scene),undefined,no));
    const carNames=["sedan","taxi","police","suv-luxury","van","truck","hatchback-sports","sedan-sports"];
    Promise.all([get("models/cars/race-future.glb"), ...carNames.map(n=>get("models/cars/"+n+".glb"))]).then(([hero,...rest])=>{
      // player car
      glowUp(hero,.45); fitTo(hero,4.8,"z"); hero.rotation.y=Math.PI;
      const holder=new THREE.Group(); holder.add(hero);
      car.children.slice().forEach(c=>{ if (c!==under && c!==flame && !c.userData.keep) c.visible=false; });
      car.add(holder);
      carWheels=[]; hero.traverse(o=>{ if (/^wheel/.test(o.name)) carWheels.push(o); });
      // traffic
      traffic.forEach((g,i)=>{ const m=rest[i%rest.length].clone(true); glowUp(m,.35); fitTo(m,4.4,"z"); m.rotation.y=Math.PI; g.children.forEach(c=>{ if (!c.userData.keep) c.visible=false; }); g.add(m); g.userData.wheels=[]; m.traverse(o=>{ if(/^wheel/.test(o.name)) g.userData.wheels.push(o); }); });
    }).catch(e=>console.warn("car models",e));
    const bNames=["building-skyscraper-a","building-skyscraper-b","building-skyscraper-c","building-skyscraper-d","building-skyscraper-e","low-detail-building-a","low-detail-building-b","low-detail-building-c","low-detail-building-wide-a"];
    Promise.all(bNames.map(n=>get("models/city/"+n+".glb"))).then(list=>{
      list.forEach(m=>glowUp(m,.3));
      const count=mobile?10:18;
      for (let i=0;i<count;i++){
        const src=list[i%list.length], m=src.clone(true), tall=i%list.length<5;
        fitTo(m, tall?26+Math.random()*16:11+Math.random()*6, "y");
        const bs=new THREE.Vector3(); new THREE.Box3().setFromObject(m).getSize(bs); if (bs.x>14) { m.scale.multiplyScalar(14/bs.x); bs.multiplyScalar(14/bs.x); m.position.y=0; m.position.y-=new THREE.Box3().setFromObject(m).min.y; }
        const side=i%2?1:-1; m.position.x=side*(13+bs.x/2+Math.random()*6); m.position.z=-LEN+(i/count)*(LEN+40);
        m.rotation.y=side>0?-Math.PI/2:Math.PI/2; scene.add(m); landmarks.push(m);
      }
    }).catch(e=>console.warn("city models",e));
  }
  if (THREE.GLTFLoader) loadModels();
  else { const sc=document.createElement("script"); sc.src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"; sc.onload=loadModels; document.head.appendChild(sc); }

  function spawnTraffic(o,z){ o.position.set(pick(LANES),0,z); o.userData.v=14; o.visible=true; }
  function spawnCoin(o,z){ o.position.set(pick(LANES),1.2,z); o.visible=true; }
  function gameStart(){
    G.on=true; G.over=false; G.lane=1; G.score=0; G.coins=0; G.near=0; G.speed=30;
    traffic.forEach((o,i)=>spawnTraffic(o,-80-i*45)); coins.forEach((o,i)=>spawnCoin(o,-40-i*30));
    G.cb("start");
  }
  function gameEnd(quit){ G.on=false; G.over=!quit; traffic.forEach(o=>o.visible=false); coins.forEach(o=>o.visible=false); G.cb(quit?"quit":"crash"); }
  function laneMove(d){ if (!G.on) return; G.lane=Math.max(0,Math.min(2,G.lane+d)); }
  // touch: swipe or tap left/right half while playing
  let tx0=null;
  addEventListener("touchstart",e=>{ if(G.on) tx0=e.touches[0].clientX; },{passive:true});
  addEventListener("touchend",e=>{ if(!G.on||tx0==null) return; const x=e.changedTouches[0].clientX, dx=x-tx0; if (Math.abs(dx)>30) laneMove(dx>0?1:-1); else laneMove(x>innerWidth/2?1:-1); tx0=null; },{passive:true});

  /* ---------- controls ---------- */
  const keys={left:false,right:false,gas:false,brake:false};
  let steer=0, carX=0, speed=22, boostT=0, lastInput=-10, t=0;
  const typing = () => { const a=document.activeElement; return a && /INPUT|SELECT|TEXTAREA/.test(a.tagName); };
  const setKey = (e, v) => {
    if (typing()) return;
    const k=e.key.toLowerCase();
    if (G.on){
      if (v && !e.repeat){ if (k==="arrowleft"||k==="a") laneMove(-1); else if (k==="arrowright"||k==="d") laneMove(1); else if (k==="escape") gameEnd(true); else if ((k==="arrowup"||k==="w")) window.SCENE.boost(); }
      if (/arrow| /.test(k)) e.preventDefault();
      return;
    }
    if (k==="arrowleft"||k==="a") keys.left=v; else if (k==="arrowright"||k==="d") keys.right=v;
    else if (k==="arrowup"||k==="w") { if (v && !keys.gas) window.SCENE.boost(); keys.gas=v; }
    else if (k==="arrowdown"||k==="s") keys.brake=v; else return;
    lastInput=t; if (/arrow/.test(k)) e.preventDefault();
  };
  addEventListener("keydown", e=>setKey(e,true)); addEventListener("keyup", e=>setKey(e,false));
  document.querySelectorAll("[data-pad]").forEach(b=>{
    const k=b.dataset.pad;
    const on=e=>{ e.preventDefault(); keys[k]=true; lastInput=t; if (k==="gas") window.SCENE.boost(); };
    const off=()=>{ keys[k]=false; };
    b.addEventListener("pointerdown",on); b.addEventListener("pointerup",off); b.addEventListener("pointerleave",off); b.addEventListener("pointercancel",off);
  });

  let mx=0,my=0,tx=0,ty=0,scrollP=0;
  addEventListener("pointermove", e=>{ mx=e.clientX/innerWidth-.5; my=e.clientY/innerHeight-.5; }, {passive:true});
  addEventListener("scroll", ()=>{ scrollP=Math.min(1, scrollY/Math.max(1,document.body.scrollHeight-innerHeight)); }, {passive:true});

  window.SCENE = { ready:true, boost(){ boostT=1.3; }, state(){ return {speed, boostT, steer, carX}; }, play:gameStart, quit:()=>gameEnd(true), game:G, onGame(f){ G.cb=f; } };

  /* bloom: neon signs, headlights and tail lights glow like a real game camera (desktop only, loaded after the scene starts) */
  let composer=null;
  function loadBloom(){
    if (mobile || reduce) return;
    const base="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/", files=["shaders/CopyShader.js","shaders/LuminosityHighPassShader.js","postprocessing/EffectComposer.js","postprocessing/RenderPass.js","postprocessing/ShaderPass.js","postprocessing/UnrealBloomPass.js"];
    const next=i=>{
      if (i>=files.length){
        try {
          const c=new THREE.EffectComposer(renderer); c.addPass(new THREE.RenderPass(scene,camera));
          c.addPass(new THREE.UnrealBloomPass(new THREE.Vector2(innerWidth,innerHeight),.55,.5,.86));
          c.setSize(innerWidth,innerHeight); composer=c;
        } catch(e){ console.warn("bloom off",e); }
        return;
      }
      const s=document.createElement("script"); s.src=base+files[i]; s.onload=()=>next(i+1); s.onerror=()=>{}; document.head.appendChild(s);
    };
    next(0);
  }
  setTimeout(loadBloom, 1200);

  function resize(){ const w=innerWidth,h=innerHeight; renderer.setSize(w,h,false); if (composer) composer.setSize(w,h); camera.aspect=w/h; camera.userData.base = w<h?74:60; camera.updateProjectionMatrix(); }
  addEventListener("resize", resize); resize();

  const clock=new THREE.Clock();
  function frame(){
    const dt=Math.min(clock.getDelta(),.05); t+=dt;
    boostT=Math.max(0,boostT-dt);
    let target;
    if (G.on){ G.speed=Math.min(90,G.speed+dt*1.2); target=G.speed+(boostT>0?25:0); }
    else target=(keys.brake?12:22)+(boostT>0?50:0)+scrollP*20;
    speed+=(target-speed)*Math.min(1,dt*3);

    let s;
    if (G.on){
      const tx=LANES[G.lane]; s=Math.max(-1,Math.min(1,(tx-carX)*.9));
      steer+=(s-steer)*Math.min(1,dt*10); carX+=(tx-carX)*Math.min(1,dt*9);
      G.score+=speed*dt*.5;
      for (const o of traffic){ const pz=o.position.z; o.position.z+=(speed-o.userData.v)*dt; if (pz<12 && o.position.z>=12 && Math.abs(o.position.x-carX)>=2 && Math.abs(o.position.x-carX)<4.6){ G.near++; G.score+=50; G.cb("near"); } if (o.position.z>40){ const far=Math.min(...traffic.map(q=>q.position.z)); spawnTraffic(o, Math.min(-160, far-32-Math.random()*25)); }
        if (Math.abs(o.position.z-12)<4 && Math.abs(o.position.x-carX)<2){ gameEnd(false); break; } }
      for (const o of coins){ o.position.z+=speed*dt; o.rotation.y+=dt*4; if (o.position.z>40) spawnCoin(o,-200-Math.random()*60);
        if (o.visible && Math.abs(o.position.z-12)<2.6 && Math.abs(o.position.x-carX)<1.8){ G.coins++; o.visible=false; G.cb("coin"); setTimeout(()=>{ if(G.on) spawnCoin(o,-200-Math.random()*60); },300); } }
    } else {
      // steering: player input, otherwise gentle auto-drive weave
      s=(keys.right?1:0)-(keys.left?1:0);
      if (s===0 && t-lastInput>3) s=Math.max(-1,Math.min(1,(Math.sin(t*.45)*3.2-carX)*.6));
      steer+=(s-steer)*Math.min(1,dt*6);
      carX=Math.max(-5,Math.min(5,carX+steer*dt*9));
    }
    car.position.x=carX; car.rotation.y=-steer*.18; car.rotation.z=steer*.06;
    car.position.y=Math.sin(t*20)*.015*(speed/22);
    wheels.forEach(w=>w.rotation.x-=speed*dt*.9);
    carWheels.forEach(w=>w.rotation.x-=speed*dt*.9);
    for (const o of traffic) if (o.visible && o.userData.wheels) o.userData.wheels.forEach(w=>w.rotation.x-=o.userData.v*dt*.9);
    for (const m of landmarks){ m.position.z+=speed*dt; if (m.position.z>60) m.position.z-=LEN+60; }
    flame.material.opacity=boostT>0?.85:0; flame.scale.y=.8+Math.random()*.5;

    gridMat.uniforms.t.value+=speed*dt*.073; sunMat.uniforms.t.value=t;
    for (let i=0;i<N;i++){
      const b=bData[i]; b.z+=speed*dt; if (b.z>40) b.z-=LEN+40;
      ps.set(b.x,b.h/2,b.z); sc.set(b.w,b.h,b.d); m4.compose(ps,q,sc); buildings.setMatrixAt(i,m4);
      const tall=b.h>34; ps.set(b.x+(b.x>0?-1:1)*(b.w/2+.05),b.h/2,b.z+b.d/2+.05); sc.set(tall?.25:0,tall?b.h:0,.25); m4.compose(ps,q,sc); glows.setMatrixAt(i,m4);
    }
    buildings.instanceMatrix.needsUpdate=true; glows.instanceMatrix.needsUpdate=true;
    for (const p of palms){ p.position.z+=speed*dt; if (p.position.z>40) p.position.z-=LEN+40; p.userData.crown.rotation.z=Math.sin(t*1.3+p.userData.sway)*.06; }
    const pa=tg.attributes.position.array;
    for (let i=0;i<TR;i++){ pa[i*3+2]+=(tv[i]>0?tv[i]+speed:tv[i]+speed)*dt*(tv[i]>0?1:.4); if (pa[i*3+2]>40) pa[i*3+2]-=LEN+40; if (pa[i*3+2]<-LEN) pa[i*3+2]+=LEN+40; }
    tg.attributes.position.needsUpdate=true;

    tx+=(mx-tx)*.05; ty+=(my-ty)*.05;
    camera.fov += ((camera.userData.base + (boostT>0?12:0)) - camera.fov)*Math.min(1,dt*4); camera.updateProjectionMatrix();
    if (G.on){ camera.position.set(carX*.7, 5.5, 24); camera.lookAt(carX*.5, 1.5, -40); }
    else { camera.position.set(carX*.55+tx*6, 4.2-ty*2+scrollP*8, 23); camera.lookAt(carX*.3+tx*4, 2.5-scrollP*2, -60); }
    if (composer) composer.render(); else renderer.render(scene,camera);
  }
  window.SCENE.tick = frame;
  if (reduce) { frame(); addEventListener("resize", frame); }
  else renderer.setAnimationLoop(frame);
})();
