(function(){
"use strict";
/* one home: send old/alternate hostnames to gamerbhai.com */
if (/(^|\.)pages\.dev$|^www\.gamerbhai\.com$|netlify\.app$/.test(location.hostname)) {
  location.replace("https://gamerbhai.com" + location.pathname.replace(/\.html$/, "").replace(/\/index$/, "/") + location.search + location.hash);
  return;
}
const S = window.SITE, PAGES = window.PAGES, LANGS = window.LANGS, T = window.T;
const PAGE = document.body.dataset.page || "home";
const reduce = (()=>{try{return localStorage.getItem("motionOff")==="1"}catch(e){return false}})(); // motion is on unless the visitor turns it off with the 🎬 button
if (reduce) document.documentElement.classList.add("calm");
const store = {
  get(k, d){ try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch(e){ return d; } },
  set(k, v){ try { localStorage.setItem(k, JSON.stringify(v)); } catch(e){} }
};
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const $ = (s, r=document) => r.querySelector(s);
const $$ = (s, r=document) => [...r.querySelectorAll(s)];

/* ---------- language ---------- */
/* language by region: visitor's own pick > country (time zone now, Cloudflare geo-check after) > browser language > English */
const CC_LANG = (() => {
  const m = {}, add = (lang, list) => list.split(" ").forEach(c => m[c] = lang);
  add("hi", "PK IN NP");
  add("zh", "CN TW HK MO");
  add("es", "ES MX AR CO CL PE VE EC GT CU BO DO HN PY SV NI CR PA UY PR GQ");
  add("ar", "SA AE EG IQ JO KW QA BH OM LB SY YE MA DZ TN LY SD PS MR");
  add("pt", "BR PT AO MZ CV GW ST TL");
  add("id", "ID MY BN");
  add("fr", "FR SN CI CM ML BF NE TG BJ GN MC HT CD CG GA MG");
  add("ru", "RU BY KZ KG");
  add("de", "DE AT LI");
  add("ja", "JP");
  return m;
})();
const TZ_CC = (() => {
  const m = {}, add = (cc, list) => list.split(" ").forEach(z => m[z] = cc);
  add("PK", "Asia/Karachi"); add("IN", "Asia/Kolkata Asia/Calcutta"); add("NP", "Asia/Kathmandu Asia/Katmandu");
  add("CN", "Asia/Shanghai Asia/Chongqing Asia/Chungking Asia/Harbin Asia/Urumqi PRC"); add("HK", "Asia/Hong_Kong"); add("TW", "Asia/Taipei"); add("MO", "Asia/Macau");
  add("SA", "Asia/Riyadh"); add("AE", "Asia/Dubai"); add("EG", "Africa/Cairo"); add("IQ", "Asia/Baghdad"); add("JO", "Asia/Amman"); add("KW", "Asia/Kuwait");
  add("QA", "Asia/Qatar"); add("BH", "Asia/Bahrain"); add("OM", "Asia/Muscat"); add("LB", "Asia/Beirut"); add("MA", "Africa/Casablanca"); add("DZ", "Africa/Algiers"); add("TN", "Africa/Tunis");
  add("BR", "America/Sao_Paulo America/Fortaleza America/Recife America/Bahia America/Manaus America/Belem America/Cuiaba America/Porto_Velho");
  add("PT", "Europe/Lisbon"); add("ID", "Asia/Jakarta Asia/Makassar Asia/Jayapura Asia/Pontianak"); add("MY", "Asia/Kuala_Lumpur Asia/Kuching");
  add("FR", "Europe/Paris"); add("RU", "Europe/Moscow Asia/Yekaterinburg Asia/Novosibirsk Asia/Vladivostok"); add("DE", "Europe/Berlin"); add("AT", "Europe/Vienna"); add("JP", "Asia/Tokyo");
  add("ES", "Europe/Madrid"); add("MX", "America/Mexico_City America/Monterrey America/Cancun America/Tijuana"); add("CO", "America/Bogota"); add("CL", "America/Santiago");
  add("PE", "America/Lima"); add("VE", "America/Caracas"); add("AR", "America/Argentina/Buenos_Aires America/Buenos_Aires America/Argentina/Cordoba");
  return m;
})();
function guessCountry(){
  const known = store.get("cc", null); if (known) return known;   // remembered from Cloudflare's geo check
  try { return TZ_CC[Intl.DateTimeFormat().resolvedOptions().timeZone] || null; } catch(e){ return null; }
}
function detectLang(){
  const saved = store.get("lang", null); if (saved && T[saved]) return saved;
  const byRegion = CC_LANG[guessCountry()]; if (byRegion && T[byRegion]) return byRegion;
  for (const l of (navigator.languages || [navigator.language || "en"])) {
    const p = l.toLowerCase().split("-")[0];
    if (p === "ur" || p === "hi") return "hi";
    if (T[p]) return p;
  }
  return "en";
}
let lang = detectLang();
const tr = k => (T[lang] && T[lang][k] != null) ? T[lang][k] : T.en[k];
const newsText = n => (n.i != null && tr("newsItems")[n.i]) || (lang === "hi" && n.hi) || n.en || "";
const locale = () => ({hi:"en-IN", zh:"zh-CN", ar:"ar", ja:"ja-JP"}[lang] || lang);
const fmtDate = iso => new Date(iso + "T00:00:00").toLocaleDateString(locale(), {day:"numeric", month:"long", year:"numeric"});

/* ---------- game state (cash / xp) ---------- */
const st = Object.assign({cash:0, xp:0, done:{}}, store.get("g6", {}));
const save = () => store.set("g6", st);
const level = () => Math.floor(st.xp / 200) + 1;

/* ---------- sound (WebAudio, original blips) ---------- */
let soundOn = store.get("sound", false), actx = null;
function beep(freqs, dur=.09, type="square", vol=.05){
  if (!soundOn) return;
  try {
    actx = actx || new (window.AudioContext || window.webkitAudioContext)();
    let t0 = actx.currentTime;
    freqs.forEach(f => { const o = actx.createOscillator(), g = actx.createGain(); o.type = type; o.frequency.value = f; g.gain.setValueAtTime(vol, t0); g.gain.exponentialRampToValueAtTime(.0001, t0 + dur); o.connect(g).connect(actx.destination); o.start(t0); o.stop(t0 + dur); t0 += dur * .8; });
  } catch(e){}
}

/* ---------- chrome: bar, hud, radar, phone, loader, footer ---------- */
function buildChrome(){
  const navLinks = PAGES.filter(p => p.id !== "home").map(p => `<a href="${p.href}" class="${p.id===PAGE?"cur":""}" data-nav="${p.nav}"></a>`).join("");
  document.body.insertAdjacentHTML("afterbegin", `
  <div class="bar"><div class="wrap">
    <a class="brand" href="index.html" aria-label="GamerBhai home"><img src="img/icons/icon-192.png" alt="" width="30" height="30"><span>GAMER<b>BHAI</b></span></a>
    <nav class="links">${navLinks}</nav>
    <div class="tools">
      <button class="iconbtn playbtn" id="playTop" data-t="gPlay"></button>
      <button class="iconbtn profbtn" id="profBtn" aria-label="Login / profile"><span>👤</span><em id="profTxt">LOGIN</em></button>
      <button class="iconbtn" id="sound" aria-label="Sound">${soundOn?"🔊":"🔈"}</button>
      <select class="iconbtn" id="langSel" aria-label="Language" style="width:auto;padding:0 8px;border-radius:999px;font:600 13px Inter,sans-serif">
        ${LANGS.map(l => `<option value="${l.code}">${esc(l.name)}</option>`).join("")}
      </select>
    </div>
  </div></div>
  <div class="hud" aria-live="polite">
    <div class="htop"><span class="hday" id="hday"></span><span class="hclock" id="hclock">00:00</span></div>
    <div class="cashwrap"><div class="cash" id="cash">$0</div><div class="cdelta" id="cdelta"></div></div>
    <div class="lvl"><span class="lvbadge" id="lvl">1</span><span class="xpbar"><i id="xp"></i></span></div>
    <div class="obj" id="obj"></div>
  </div>
  <div class="lvup" id="lvup"><small>LEVEL UP</small><b id="lvupN"></b></div>
  <div class="radar" aria-label="Map"><div class="rmap" id="rmap"></div><div class="rring"></div><b class="rn" id="rn">N</b><div class="sweep"></div><div class="you" id="you"></div>
    ${PAGES.filter(p=>p.id!=="home").map(p => `<button class="blip ${p.id===PAGE?"cur":(st.done["visit-"+p.id]?"done":"new")}" style="left:${p.pos[0]}%;top:${p.pos[1]}%" data-href="${p.href}" data-navlabel="${p.nav}" aria-label=""></button>`).join("")}
  </div>
  <div class="rbars" aria-hidden="true"><span class="rb spd"><i id="rSpd"></i></span><span class="rb nos"><i id="rNos"></i></span></div>
  <button class="phonebtn" id="phoneBtn" aria-label="Menu">📱</button>
  <div class="phone" id="phone"><div class="notch"></div><div class="ptime" id="ptime"></div><div class="apps">
    ${PAGES.map(p => `<a class="app" href="${p.href}"><span>${p.icon}</span><em data-nav="${p.nav}" style="font-style:normal"></em></a>`).join("")}
  </div></div>
  <div class="loader" id="loader">
    <div class="wipe w1"></div><div class="wipe w2"></div><div class="wipe w3"></div>
    <div class="speed"></div><div class="road"></div>
    <div class="lcard">
      <div class="lk" id="loadK"></div>
      <div class="lt" id="loadT"></div>
      <div class="tip"><b>💡</b><span id="loadTip"></span></div>
      <div class="lrow"><div class="lbar"><i id="lfill"></i><span class="lcar" id="lcar"></span></div><b class="lpct" id="lpct">0%</b></div>
    </div>
    <div class="wheel"></div>
  </div>
  <div class="arrive" id="arrive"><small>📍</small><b id="arriveT"></b></div>
  <div class="toasts" id="toasts"></div>
  <div class="gfx" id="gfx"><div class="vig"></div><div class="streaks"></div><div class="flash" id="gflash"></div></div>
  <div class="ghud" id="ghud">
    <div class="gs score"><span data-t="gScore"></span><b id="gScore">0</b><em class="pb" id="gPb"></em></div>
    <div class="gs"><span>💵</span><b id="gCoins">0</b></div>
    <button class="iconbtn" id="gQuit" aria-label="Quit">✕</button>
  </div>
  <div class="gpop" id="gpop"></div>
  <div class="gcount" id="gcount"></div>
  <div class="speedo" id="speedo"><div class="dial" id="sdial"></div><div class="sread"><b id="skmh">0</b><small>km/h</small></div><div class="snos"><i id="snos"></i></div></div>
  <div class="gpanel" id="gpanel" role="dialog" aria-modal="true"><div class="gbox">
    <div class="gtag" id="gTag">MISSION</div>
    <div class="gtitle" id="gTitle" data-text=""></div>
    <div class="grank" id="gRank"></div>
    <p class="gtext" data-t="gHow"></p>
    <div class="gkeys" id="gKeys"><kbd>←</kbd><kbd>→</kbd><span>/</span><kbd>A</kbd><kbd>D</kbd><span>·</span><kbd>W</kbd><span>NITRO</span></div>
    <div class="gstats" id="gStats"></div>
    <div class="grec" id="gRec">★ NEW RECORD ★</div>
    <div class="gworld" id="gWorld"></div>
    <div class="gname" id="gNameRow"><label for="gNick">🏷 NAME</label><input id="gNick" maxlength="16" autocomplete="nickname" spellcheck="false"></div>
    <div class="glb" id="gLb"><div class="glbh">🏆 WORLD TOP 10</div><ol id="gLbList"><li class="muted">…</li></ol></div>
    <div class="gbtns"><button class="btn primary" id="gGo"></button><button class="btn" id="gBack" data-t="gBack"></button></div>
    <button class="gsup" id="gSup" hidden>☕ Enjoying Neon Run? Support the site</button>
    <div class="ghint"><kbd>Enter</kbd> ▶ &nbsp; <kbd>Esc</kbd> ✕</div>
  </div></div>`);
  $("main").insertAdjacentHTML("afterend", `<footer><div class="wrap">
    <nav>${PAGES.map(p => `<a href="${p.href}" data-nav="${p.nav}"></a>`).join("")}</nav>
    <p data-t="footer1"></p><p data-t="footer2"></p><button class="btn support" id="supFoot" hidden>☕ Support the site</button> <a class="btn ytbtn" href="https://www.youtube.com/@gamerbhaicom" target="_blank" rel="noopener">▶ YouTube</a> <button class="motionbtn" id="motionBtn">🎬 Animations: ${reduce?"OFF":"ON"}</button></div></footer>`);

  $("#langSel").value = lang;
  $("#langSel").addEventListener("change", e => {
    lang = e.target.value; store.set("lang", lang); applyText(); renderPage(); transBar();
    reward("lang", tr("mLang"), LANGS.find(l=>l.code===lang).name, 20, 20);
  });
  $("#motionBtn").addEventListener("click", () => { try { localStorage.setItem("motionOff", reduce ? "0" : "1"); } catch(e){} location.reload(); });
  $("#sound").addEventListener("click", () => { soundOn = !soundOn; store.set("sound", soundOn); $("#sound").textContent = soundOn ? "🔊" : "🔈"; beep([660, 880]); });
  $$(".blip").forEach(b => b.addEventListener("click", () => go(b.dataset.href)));
  $("#phoneBtn").addEventListener("click", e => { e.stopPropagation(); $("#phone").classList.toggle("open"); beep([520, 780], .07, "sine"); });
  document.addEventListener("click", e => { if (!e.target.closest("#phone")) $("#phone").classList.remove("open"); });
  const tick = () => { $("#ptime").textContent = new Date().toLocaleTimeString(locale(), {hour:"2-digit", minute:"2-digit"}); };
  tick(); setInterval(tick, 30000);
}

function applyText(){
  const L = LANGS.find(l => l.code === lang) || LANGS[0];
  document.documentElement.lang = lang === "hi" ? "en" : lang;
  document.body.dir = L.rtl ? "rtl" : "ltr";
  $$("[data-t]").forEach(el => { const v = tr(el.dataset.t); if (typeof v === "string") el.textContent = v; });
  $$("[data-nav]").forEach(el => { el.textContent = tr(el.dataset.nav); });
  $$("[data-navlabel]").forEach(el => { el.dataset.label = tr(el.dataset.navlabel); el.setAttribute("aria-label", tr(el.dataset.navlabel)); });
  const page = PAGES.find(p => p.id === PAGE);
  // English keeps the hand-written SEO title from the HTML; other languages get a translated one
  if (!window.__seoTitle) window.__seoTitle = document.title;
  if (page && !document.body.dataset.seo) document.title = lang === "en" ? window.__seoTitle : (PAGE === "home" ? "GTA 6" : tr(page.nav) + " – GTA 6") + " | GamerBhai";
  updateHud(false);
}

/* ---------- HUD + missions ---------- */
let shownCash = st.cash;
function updateHud(animate=true){
  const el = $("#cash"); if (!el) return;
  const target = st.cash;
  if (!animate || reduce) { shownCash = target; el.textContent = "$" + target.toLocaleString("en"); }
  else {
    const from = shownCash, t0 = performance.now();
    const step = now => { const p = Math.min(1, (now - t0) / 700); shownCash = Math.round(from + (target - from) * p); el.textContent = "$" + shownCash.toLocaleString("en"); if (p < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step); el.classList.remove("pop"); void el.offsetWidth; el.classList.add("pop");
  }
  const lv = level();
  $("#lvl").textContent = lv;
  $("#xp").style.width = ((st.xp % 200) / 2) + "%";
  const found = PAGES.filter(p => st.done["visit-" + p.id]).length;
  $("#obj").innerHTML = `<span>📍</span> ${found}/${PAGES.length}`;
  $("#obj").classList.toggle("full", found === PAGES.length);
  if (animate && target > hudCash) cashDelta(target - hudCash);
  hudCash = target;
  if (lv > hudLevel && animate) levelUp(lv);
  hudLevel = lv;
}
let hudCash = st.cash, hudLevel = level(), lastBoost = 0;
function cashDelta(n){
  if (reduce) return;
  const d = document.createElement("div"); d.className = "cd"; d.textContent = "+$" + n.toLocaleString("en");
  $("#cdelta").appendChild(d); setTimeout(() => d.remove(), 1400);
}
function levelUp(lv){
  const b = $("#lvup"); $("#lvupN").textContent = "LV " + lv;
  b.classList.remove("show"); void b.offsetWidth; b.classList.add("show");
  beep([523, 659, 784, 1046, 1318], .12, "triangle", .06);
  setTimeout(() => b.classList.remove("show"), 2600);
}
/* live HUD clock + radar driven by the 3D car */
function hudLoop(){
  const days = ["SUN","MON","TUE","WED","THU","FRI","SAT"];
  const clock = () => { const d = new Date(); $("#hclock").textContent = String(d.getHours()).padStart(2,"0") + ":" + String(d.getMinutes()).padStart(2,"0"); $("#hday").textContent = days[d.getDay()]; };
  clock(); setInterval(clock, 15000);
  const map = $("#rmap"), you = $("#you"), spd = $("#rSpd"), nos = $("#rNos");
  if (!map) return;
  let off = 0, lastY = scrollY, last = performance.now(), rot = 0;
  const tick = now => {
    const dt = Math.min(.1, (now - last) / 1000); last = now;
    const s = window.SCENE && window.SCENE.state ? window.SCENE.state() : {speed:20, boostT:0, steer:0};
    off += s.speed * dt * 1.6 + (scrollY - lastY) * .25; lastY = scrollY;
    rot += ((-s.steer * 14) - rot) * Math.min(1, dt * 6);
    map.style.transform = `rotate(${rot.toFixed(2)}deg)`;
    map.style.backgroundPosition = `0 ${off.toFixed(1)}px`;
    you.style.transform = `rotate(${(s.steer * 18).toFixed(1)}deg)`;
    spd.style.width = Math.min(100, s.speed / 1.15) + "%";
    spd.parentNode.classList.toggle("hot", s.speed > 60);
    const since = Date.now() - lastBoost;
    nos.style.width = (s.boostT > 0 ? s.boostT / 1.3 * 100 : Math.min(100, since / 40)) + "%";
    nos.parentNode.classList.toggle("ready", s.boostT <= 0 && since >= 4000);
    if (!reduce) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}
function toast(title, msg, cash){
  const box = $("#toasts"); if (!box) return;
  const d = document.createElement("div"); d.className = "toast";
  d.innerHTML = `<div class="tt">${esc(title)}</div><div class="tm">${esc(msg)}</div>${cash?`<div class="tr">+$${cash} · +XP</div>`:""}`;
  box.appendChild(d); setTimeout(() => d.remove(), 3200);
}
function reward(key, title, msg, cash, xp){
  if (st.done[key]) return false;
  st.done[key] = 1; st.cash += cash; st.xp += xp; save();
  toast(title, msg, cash); updateHud(); beep([523, 659, 784, 1046], .1, "triangle", .06);
  return true;
}

/* ---------- transitions ---------- */
const ss = { get(k){ try { return sessionStorage.getItem(k); } catch(e){ return null; } }, set(k,v){ try { sessionStorage.setItem(k,v); } catch(e){} } };
function pageName(href){
  const k = href.replace(/^\//, "").replace(/\.html$/, "") || "index";
  const p = PAGES.find(x => x.href.replace(/\.html$/, "") === k);
  if (p) return p.id === "home" ? "GAMERBHAI" : tr(p.nav);
  const m = href.match(/gta-6-price-in-([a-z-]+)/);
  return m ? m[1].replace(/-/g, " ") : "GAMERBHAI";
}
function fillLoader(title, kicker){
  const tips = tr("tips");
  $("#loadK").textContent = kicker || tr("loading");
  $("#loadT").textContent = title;
  $("#loadTip").textContent = tips[(Math.random() * tips.length) | 0];
}
let pctRaf = 0;
function runPct(from, to, ms, done){
  clearInterval(pctRaf);
  const t0 = Date.now(), f = $("#lfill"), c = $("#lcar"), n = $("#lpct");
  let fired = false;
  const step = () => {
    const p = Math.min(1, (Date.now() - t0) / ms), e = 1 - Math.pow(1 - p, 3), v = from + (to - from) * e;
    f.style.width = v + "%"; c.style.left = v + "%"; n.textContent = Math.round(v) + "%";
    if (p >= 1) { clearInterval(pctRaf); if (done && !fired) { fired = true; done(); } }
  };
  step(); pctRaf = setInterval(step, 16);
}
function go(href){
  if (reduce) { location.href = href; return; }
  const L = $("#loader"); if (L.classList.contains("on")) return;
  window.SCENE && window.SCENE.boost();
  beep([180, 360, 720, 1100], .07, "sawtooth", .035);
  fillLoader(pageName(href));
  L.classList.remove("out"); L.classList.add("on");
  runPct(0, 100, 820, () => { ss.set("arrive", "1"); location.href = href; });
}
/* arriving on a page: start covered, sweep panels away, drop the location banner */
function arriveIn(){
  if (reduce) return;
  const L = $("#loader"), first = !ss.get("booted"), fromNav = ss.get("arrive");
  ss.set("arrive", ""); ss.set("booted", "1");
  const banner = () => {
    const h = PAGES.find(p => p.id === PAGE);
    $("#arriveT").textContent = h ? (h.id === "home" ? "GAMERBHAI" : tr(h.nav)) : (document.body.dataset.country || ($("h1") && $("h1").textContent) || "");
    const a = $("#arrive"); a.classList.remove("show"); void a.offsetWidth; a.classList.add("show");
    beep([392, 523], .09, "triangle", .04);
    setTimeout(() => a.classList.remove("show"), 2200);
  };
  const reveal = () => { L.classList.add("out"); setTimeout(() => { L.classList.remove("on", "out"); }, 650); banner(); };
  if (first) {
    // first visit this session: boot screen, bar follows real loading
    fillLoader("GAMERBHAI", "▶ BOOTING");
    L.classList.add("on", "boot");
    const start = performance.now();
    runPct(0, 72, 900);
    const finish = () => runPct(72, 100, 450, () => setTimeout(() => { L.classList.remove("boot"); reveal(); }, 150));
    const ready = () => setTimeout(finish, Math.max(0, 1100 - (performance.now() - start)));
    if (document.readyState === "complete") ready(); else addEventListener("load", ready, { once: true });
    setTimeout(() => { if (L.classList.contains("boot")) finish(); }, 4500);
  } else if (fromNav) {
    fillLoader(""); $("#lfill").style.width = "100%"; $("#lpct").textContent = "100%"; $("#lcar").style.left = "100%";
    L.classList.add("on", "instant");
    requestAnimationFrame(() => requestAnimationFrame(() => { L.classList.remove("instant"); reveal(); }));
  }
}
document.addEventListener("click", e => {
  const a = e.target.closest("a[href]");
  const h = a && a.getAttribute("href");
  if (a && !a.target && !e.ctrlKey && !e.metaKey && !e.shiftKey && (h === "/" || /^\/?[a-z0-9-]+(\.html)?$/.test(h))) {
    const norm = x => { x = x.replace(/^\//, "").replace(/\.html$/, ""); return x === "" || x === "index" ? "index" : x; };
    if (norm(h) === norm(location.pathname.split("/").pop())) return;
    e.preventDefault(); go(h);
  }
});
addEventListener("pageshow", e => { const l = $("#loader"); if (l && e.persisted) { clearInterval(pctRaf); l.classList.remove("on", "out", "boot"); } });

/* click ripple */
document.addEventListener("pointerdown", e => {
  if (reduce) return;
  const r = document.createElement("div"); r.className = "ripple"; r.style.left = e.clientX + "px"; r.style.top = e.clientY + "px";
  document.body.appendChild(r); setTimeout(() => r.remove(), 600);
  if (e.target.closest("button,a,.pc,summary")) beep([880], .04, "square", .025);
});
/* menu hover tick, like moving a cursor over game menu items */
let lastHover = null, lastHoverT = 0;
document.addEventListener("pointerover", e => {
  if (e.pointerType !== "mouse") return;
  const el = e.target.closest(".btn,.links a,.iconbtn,.area,.pc,.app,.seg button,summary,.blip,.phonebtn,.brand");
  if (!el || el === lastHover) return;
  lastHover = el;
  const n = performance.now(); if (n - lastHoverT < 70) return; lastHoverT = n;
  beep([1320], .025, "square", .012);
});
document.addEventListener("pointerout", e => { if (lastHover && !lastHover.contains(e.relatedTarget)) lastHover = null; });
function plus(x, y, text){
  if (reduce) return;
  const p = document.createElement("div"); p.className = "plus"; p.textContent = text; p.style.left = x + "px"; p.style.top = y + "px";
  document.body.appendChild(p); setTimeout(() => p.remove(), 900);
}

/* ---------- tilt + reveal ---------- */
function bindTilt(){
  if (reduce || !matchMedia("(hover:hover)").matches) return;
  $$(".tilt:not([data-b])").forEach(el => {
    el.dataset.b = 1;
    el.addEventListener("pointermove", e => { const r = el.getBoundingClientRect(); const x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5; el.style.transform = `perspective(800px) rotateY(${x*10}deg) rotateX(${-y*10}deg)`; });
    el.addEventListener("pointerleave", () => { el.style.transform = ""; });
  });
}
const io = "IntersectionObserver" in window ? new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), {threshold:.12}) : null;
function bindReveal(){ $$(".reveal:not(.in)").forEach(el => io ? io.observe(el) : el.classList.add("in")); }

function countTo(el, target, fmt = v => Math.round(v).toLocaleString("en")){
  if (!el) return;
  if (reduce) { el.textContent = fmt(target); return; }
  const from = parseFloat(el.dataset.v || 0), t0 = performance.now(); el.dataset.v = target;
  const step = now => { const p = Math.min(1, (now - t0) / 900), e = 1 - Math.pow(1 - p, 3); el.textContent = fmt(from + (target - from) * e); if (p < 1) requestAnimationFrame(step); };
  requestAnimationFrame(step);
}

/* ---------- currency helpers ---------- */
const REGION_CUR = {US:"USD",GB:"GBP",PK:"PKR",IN:"INR",CN:"CNY",AE:"AED",SA:"SAR",BD:"BDT",TR:"TRY",JP:"JPY",KR:"KRW",BR:"BRL",MX:"MXN",CA:"CAD",AU:"AUD",RU:"RUB",ID:"IDR",MY:"MYR",NG:"NGN",EG:"EGP",ZA:"ZAR",PH:"PHP",SG:"SGD",TH:"THB",VN:"VND",QA:"QAR",KW:"KWD",OM:"OMR",BH:"BHD",NZ:"NZD",HK:"HKD",TW:"TWD",CH:"CHF",SE:"SEK",NO:"NOK",PL:"PLN",AR:"ARS",CL:"CLP",CO:"COP",DE:"EUR",FR:"EUR",IT:"EUR",ES:"EUR",NL:"EUR",BE:"EUR",AT:"EUR",IE:"EUR",PT:"EUR",FI:"EUR",GR:"EUR",NP:"NPR",LK:"LKR",AF:"AFN",IR:"IRR",IQ:"IQD",JO:"JOD",MA:"MAD",DZ:"DZD",KE:"KES",UA:"UAH",KZ:"KZT",UZ:"UZS",PE:"PEN"};
const TZ_CUR = {"Asia/Karachi":"PKR","Asia/Kolkata":"INR","Asia/Calcutta":"INR","Asia/Shanghai":"CNY","Asia/Dhaka":"BDT","Asia/Dubai":"AED","Asia/Riyadh":"SAR","Asia/Jakarta":"IDR","Asia/Tokyo":"JPY","Europe/London":"GBP","Europe/Istanbul":"TRY","Europe/Moscow":"RUB","America/Sao_Paulo":"BRL","America/Mexico_City":"MXN","Africa/Lagos":"NGN","Africa/Cairo":"EGP","Asia/Manila":"PHP","Asia/Kathmandu":"NPR"};
function detectCurrency(rates){
  const saved = store.get("cur", null); if (saved && rates[saved]) return saved;
  try { const tz = Intl.DateTimeFormat().resolvedOptions().timeZone; if (TZ_CUR[tz] && rates[TZ_CUR[tz]]) return TZ_CUR[tz]; } catch(e){}
  for (const l of (navigator.languages || [navigator.language || ""])) { const r = (l.split("-")[1] || "").toUpperCase(); if (REGION_CUR[r] && rates[REGION_CUR[r]]) return REGION_CUR[r]; }
  return "USD";
}
const money = (v, cur) => { const d = v >= 1000 ? 0 : 2; try { return new Intl.NumberFormat(locale(), {style:"currency", currency:cur, minimumFractionDigits:d, maximumFractionDigits:d}).format(v); } catch(e) { return cur + " " + v.toFixed(d); } };
const curName = cur => { try { return new Intl.DisplayNames([locale()], {type:"currency"}).of(cur); } catch(e) { return cur; } };
async function loadRates(){
  const c = store.get("rates", null);
  if (c && Date.now() - c.at < 6 * 3600e3) return c;
  try {
    const r = await fetch("https://open.er-api.com/v6/latest/USD"); const j = await r.json();
    if (j && j.result === "success" && j.rates) { const v = {rates:j.rates, at:Date.now(), live:true, updated:j.time_last_update_utc}; store.set("rates", v); return v; }
  } catch(e){}
  return c || {rates:S.fallbackRates, at:0, live:false};
}

/* ---------- page renderers ---------- */
const R = {};
R.home = () => {
  $("#releaseDate").textContent = fmtDate(S.consoleRelease);
  const days = Math.max(0, Math.floor((Date.now() - new Date(S.consoleRelease + "T00:00:00")) / 864e5));
  countTo($("#daysSince"), days);
  $("#explore").innerHTML = PAGES.filter(p => p.desc).map(p => `<a class="glass tilt area reveal" href="${p.href}"><div class="pop"><div class="ic">${p.icon}</div><h3>${esc(tr(p.nav))}</h3><p>${esc(tr(p.desc))}</p><div class="go">${esc(tr("go"))}</div></div></a>`).join("");
  $("#latest").innerHTML = S.news.slice(0, 3).map(n => `<li><span class="d">${fmtDate(n.date)}</span>${esc(newsText(n))}</li>`).join("");
};

let P = { ed: store.get("ed", "std"), custom: 50, cur: "USD", rates: null };
R.price = async () => {
  if (!P.rates) {
    $("#rateInfo").textContent = "…";
    const r = await loadRates(); P.rates = r; P.cur = detectCurrency(r.rates); P.detected = P.cur;
  }
  const rates = P.rates.rates;
  const codes = Object.keys(rates).sort((a, b) => curName(a).localeCompare(curName(b), locale()));
  $("#curSel").innerHTML = codes.map(c => `<option value="${c}">${esc(curName(c))} (${c})</option>`).join("");
  $("#curSel").value = P.cur;
  $$("#edSeg button").forEach(b => b.classList.toggle("on", b.dataset.ed === P.ed));
  $("#customWrap").style.display = P.ed === "custom" ? "" : "none";
  $("#customAmt").value = P.custom;
  $("#detected").textContent = tr("detected") + ": " + P.detected;
  $("#rateInfo").textContent = P.rates.live ? `${tr("ratesLive")} ${new Date(P.rates.at).toLocaleString(locale())} · open.er-api.com` : tr("ratesOffline");
  calc(false);
};
function usd(){ return P.ed === "custom" ? Math.max(0, parseFloat(P.custom) || 0) : S.editions[P.ed]; }
function calc(rewardIt = true){
  const rates = P.rates.rates, v = usd() * (rates[P.cur] || 1);
  countTo($("#amt"), v, x => money(x, P.cur));
  $("#amtSub").textContent = `${money(usd(), "USD")} · ${P.ed === "custom" ? tr("custom") : tr(P.ed)} · 1 USD = ${(rates[P.cur] || 1).toLocaleString(locale(), {maximumFractionDigits:4})} ${P.cur}`;
  $("#pops").innerHTML = S.popular.filter(c => rates[c]).map(c => `<button class="pc ${c===P.cur?"on":""}" data-c="${c}"><div class="c">${c}</div><div class="p">${esc(money(usd() * rates[c], c))}</div></button>`).join("");
  $$("#pops .pc").forEach(b => b.addEventListener("click", e => { P.cur = b.dataset.c; store.set("cur", P.cur); $("#curSel").value = P.cur; calc(); plus(e.clientX, e.clientY, P.cur); }));
  if (rewardIt) reward("price-" + P.cur, tr("mPrice"), curName(P.cur), 50, 30);
}
function bindPrice(){
  $$("#edSeg button").forEach(b => b.addEventListener("click", () => { P.ed = b.dataset.ed; store.set("ed", P.ed); $$("#edSeg button").forEach(x => x.classList.toggle("on", x === b)); $("#customWrap").style.display = P.ed === "custom" ? "" : "none"; calc(); }));
  $("#curSel").addEventListener("change", e => { P.cur = e.target.value; store.set("cur", P.cur); calc(); });
  $("#customAmt").addEventListener("input", e => { P.custom = e.target.value; calc(false); });
}

R.pc = () => {
  $("#hist").innerHTML = S.history.map(h => {
    const a = new Date(h.console), b = new Date(h.pc), m = Math.round((b - a) / (864e5 * 30.44));
    return `<tr><td>${esc(h.game)}</td><td>${fmtDate(h.console)}</td><td>${fmtDate(h.pc)}</td><td><b>${m} ${esc(tr("months"))}</b></td></tr>`;
  }).join("");
  $("#waitList").innerHTML = tr("wait").map(w => `<li>${esc(w)}</li>`).join("");
};

R.trailers = () => {
  $("#tvs").innerHTML = S.trailers.map((id, i) => `<div class="glass tilt"><button class="tv" data-id="${esc(id)}" aria-label="${esc(tr("play"))} ${i+1}"><img src="https://i.ytimg.com/vi/${esc(id)}/hqdefault.jpg" alt="" loading="lazy"><span class="play"><span></span></span></button><div class="tvlabel">Trailer ${i+1}</div></div>`).join("");
  $$(".tv").forEach(b => b.addEventListener("click", () => {
    if (b.querySelector("iframe")) return;
    b.insertAdjacentHTML("beforeend", `<iframe src="https://www.youtube-nocookie.com/embed/${b.dataset.id}?autoplay=1&rel=0" title="GTA 6 trailer" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>`);
    reward("tv-" + b.dataset.id, tr("mTrailer"), b.parentElement.querySelector(".tvlabel").textContent, 100, 50);
  }));
};

R.faq = () => {
  $("#faqList").innerHTML = tr("faq").map(([q, a], i) => `<details data-i="${i}"><summary>${esc(q)}</summary><p>${esc(a)}</p></details>`).join("");
  $$("#faqList details").forEach(d => d.addEventListener("toggle", () => { if (d.open) reward("faq-" + d.dataset.i, tr("mFaq"), d.querySelector("summary").textContent, 10, 15); }));
  $("#scamList").innerHTML = tr("scams").map(s => `<li>${esc(s)}</li>`).join("");
};

R.news = () => { R.newsWeb();
  $("#newsList").innerHTML = S.news.map(n => `<li><span class="d">${fmtDate(n.date)}</span>${esc(newsText(n))}${n.link ? ` <a href="${esc(n.link)}"${n.link[0] === "/" ? "" : ' target="_blank" rel="noopener"'}>${n.link[0] === "/" ? "→" : "↗"}</a>` : ""}</li>`).join("");
};
R.newsWeb = () => {
  const box = $("#newsWeb"); if (!box) return;
  fetch("headlines.json?t=" + Math.floor(Date.now() / 6e5)).then(r => r.ok ? r.json() : null).then(d => {
    if (!d || !d.items || !d.items.length) return;
    box.innerHTML = `<h2><span class="n">🌐</span>Around the web</h2><div class="glass"><ul class="news webnews">${d.items.map(i => `<li><span class="d">${fmtDate(i.d)}</span><a href="${esc(i.u)}" target="_blank" rel="noopener nofollow">${esc(i.t)}</a> <small>${esc(i.s)}</small></li>`).join("")}</ul><p class="note">Headlines update automatically every few hours. Links open the original sites.</p></div>`;
  }).catch(() => {});
};
R.about = () => {};

/* country pages + countries hub: swap build-time prices for live ones */
async function livePrices(){
  const r = await loadRates(); if (!r.live) return;
  $$("[data-usd][data-cur]").forEach(el => { const c = el.dataset.cur; if (r.rates[c]) el.textContent = money(parseFloat(el.dataset.usd) * r.rates[c], c); });
  const ci = $("#cRate"); if (ci && r.rates[ci.dataset.cur]) ci.textContent = `1 USD = ${r.rates[ci.dataset.cur].toLocaleString(locale(), {maximumFractionDigits:4})} ${ci.dataset.cur} · ${tr("ratesLive")} ${new Date(r.at).toLocaleString(locale())} · open.er-api.com`;
}
R.countries = () => { livePrices(); };
R.country = () => {
  livePrices();
  $$("details").forEach((d, i) => d.addEventListener("toggle", () => { if (d.open) reward("cfaq-" + i, tr("mFaq"), d.querySelector("summary").textContent, 10, 15); }));
};

function renderPage(){ (R[PAGE] || (() => {}))(); bindTilt(); bindReveal(); }

/* ---------- mini-game UI: Neon Run ---------- */
/* ---------- world leaderboard (Supabase, anonymous players + nickname) ---------- */
const GOOGLE_LOGIN = true;    // flip to true once the Google provider is enabled in Supabase
/* ---------- MONEY: switch on by filling these in (no other code changes needed) ---------- */
const MONEY = {
  adsense: "",            // AdSense publisher ID after approval, e.g. "ca-pub-1234567890123456"
  adsenseSlot: "",        // optional display ad-unit slot ID (auto ads work without it)
  noAdPages: ["story", "guides", "community", "game"],   // pages with Rockstar screenshots / user content stay ad-free
  eneba: "",              // Eneba affiliate link to GTA 6 (from your Eneba/AWIN dashboard)
  amazon: ""              // Amazon Associates link to GTA 6 / PS5 (optional)
};
const LB_CFG = { url: "https://wnzqjmvlfnrkwswcbpyk.supabase.co", key: "sb_publishable_qY_rBY_6XccjN6X-pWhVig_h2dGue_5" };   // public (publishable) key - safe in browser code
const LB = {
  on: !!(LB_CFG.url && LB_CFG.key), sb: null, ready: null, run: null,
  init(){
    if (!this.on) return Promise.resolve(false);
    if (this.ready) return this.ready;
    this.ready = new Promise(res => {
      const go = async () => {
        try {
          this.sb = window.supabase.createClient(LB_CFG.url, LB_CFG.key, { auth: { persistSession: true, storageKey: "g6-auth" } });
          const { data } = await this.sb.auth.getSession();
          if (!data.session) { const { data: d2, error } = await this.sb.auth.signInAnonymously(); if (error) throw error; this.uid = d2 && d2.user && d2.user.id; } else this.uid = data.session.user.id;
          res(true);
        } catch(e) { console.warn("leaderboard", e); this.on = false; res(false); }
      };
      if (window.supabase) go();
      else { const s = document.createElement("script"); s.src = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"; s.onload = go; s.onerror = () => { this.on = false; res(false); }; document.head.appendChild(s); }
    });
    return this.ready;
  },
  async start(){ this.run = null; if (!(await this.init())) return; const { data, error } = await this.sb.rpc("start_run"); if (!error) this.run = data; },
  async submit(name, score, coins, near){
    if (!(await this.init()) || !this.run) return null;
    const run = this.run; this.run = null;
    const { data, error } = await this.sb.rpc("submit_score", { p_run: run, p_name: name, p_score: Math.floor(score), p_coins: coins, p_near: near });
    if (error) { console.warn("score", error.message); return null; }
    return data;
  },
  async members(){ if (!(await this.init())) return null; const { data, error } = await this.sb.rpc("get_member_count"); return error ? null : Number(data); },
  ticket(){ return this.uid ? this.uid.slice(0, 8).toUpperCase() : null; },
  async account(){ if (!(await this.init())) return null; const { data } = await this.sb.auth.getUser(); const u = data && data.user; if (!u) return null; this.uid = u.id; const g = (u.identities || []).find(i => i.provider === "google"); return { anon: !!u.is_anonymous && !g, email: g ? (u.email || (g.identity_data || {}).email || "") : "" }; },
  async google(){
    if (!(await this.init())) return;
    const back = location.origin + location.pathname;
    // keep this browser's progress: attach Google to the current (anonymous) player first
    const r = await this.sb.auth.linkIdentity({ provider: "google", options: { redirectTo: back } });
    if (r.error) await this.sb.auth.signInWithOAuth({ provider: "google", options: { redirectTo: back } });
  },
  async logout(){ if (!(await this.init())) return; await this.sb.auth.signOut(); location.reload(); },
  async top(n = 10){ if (!(await this.init())) return null; const { data, error } = await this.sb.rpc("get_leaderboard", { p_limit: n }); return error ? null : data; }
};
function nickname(){
  let n = store.get("nick", "");
  if (!n) { n = "Player" + Math.floor(1000 + Math.random() * 9000); store.set("nick", n); }
  return n;
}
async function renderBoard(){
  const box = $("#gLb"), list = $("#gLbList");
  if (!LB.on) { box.style.display = "none"; $("#gNameRow").style.display = "none"; return; }
  const rows = await LB.top(10);
  if (!rows) { box.style.display = "none"; return; }
  box.style.display = "";
  list.innerHTML = rows.length
    ? rows.map(r => `<li class="${r.me ? "me" : ""}"><span class="lr">${r.rank}</span><span class="ln">${esc(r.name)}</span><b>${Number(r.score).toLocaleString("en")}</b></li>`).join("")
    : `<li class="muted">Be the first! 🏁</li>`;
}

function bindGame(){
  const SC = window.SCENE; if (!SC || !SC.play) { $("#playTop").style.display = "none"; return; }
  const panel = $("#gpanel");
  const ctas = $(".hero .ctas");
  if (ctas) ctas.insertAdjacentHTML("afterbegin", `<button class="btn primary glow" id="playHero" data-t="gPlay">${esc(tr("gPlay"))}</button>`);
  let pending = null, timer = null, best = store.get("best", 0), counting = false, starting = false, pbShown = false, combo = 0, comboT = 0;
  const fmt = n => Math.floor(n).toLocaleString("en");
  const rankOf = s => s >= 3000 ? "S" : s >= 1800 ? "A" : s >= 900 ? "B" : s >= 350 ? "C" : "D";
  const pop = (txt, cls) => { if (reduce) return; const d = document.createElement("div"); d.className = "gp " + (cls || ""); d.textContent = txt; $("#gpop").appendChild(d); setTimeout(() => d.remove(), 1100); };
  const flash = cls => { const f = $("#gflash"); f.className = "flash"; void f.offsetWidth; f.className = "flash " + cls; };
  const countUp = (el, to, ms, pre) => new Promise(res => {
    if (reduce || !to) { el.textContent = (pre || "") + fmt(to); return res(); }
    const t0 = Date.now(); let lastTick = 0;
    const iv = setInterval(() => {
      const p = Math.min(1, (Date.now() - t0) / ms);
      el.textContent = (pre || "") + fmt(to * (1 - Math.pow(1 - p, 3)));
      if (Date.now() - lastTick > 60) { lastTick = Date.now(); beep([880 + p * 600], .02, "square", .015); }
      if (p >= 1) { clearInterval(iv); res(); }
    }, 16);
  });
  const showPanel = async (crashed) => {
    const G = SC.game, sc = Math.floor(G.score);
    $("#gTag").textContent = crashed ? "RUN OVER" : "MISSION";
    const t = crashed ? tr("gCrash") : tr("gReady");
    $("#gTitle").textContent = t; $("#gTitle").dataset.text = t;
    $("#gTitle").classList.toggle("crash", !!crashed);
    panel.classList.toggle("crashed", !!crashed);
    $("#gGo").textContent = crashed ? tr("gAgain") : tr("gPlay");
    $("#gRank").textContent = ""; $("#gRank").className = "grank";
    $("#gRec").classList.remove("on");
    $("#gKeys").style.display = crashed ? "none" : "";
    panel.classList.add("on"); document.body.classList.add("gaming");
    $("#gNick").value = nickname(); $("#gWorld").textContent = "";
    if (!crashed) renderBoard();
    setTimeout(() => $("#gGo").focus(), 50);
    if (!crashed) { $("#gStats").innerHTML = `<div><span>${esc(tr("gBest"))}</span><b>${fmt(best)}</b></div>`; return; }
    const isRec = G._rec && sc > 0;
    $("#gStats").innerHTML = `<div><span>${esc(tr("gScore"))}</span><b id="gsS">0</b></div><div><span>💵 ${esc(tr("gCash"))}</span><b id="gsC">$0</b></div><div><span>⚡ NEAR MISS</span><b id="gsN">0</b></div><div><span>${esc(tr("gBest"))}</span><b>${fmt(best)}</b></div>`;
    counting = true;
    await countUp($("#gsS"), sc, 700);
    await countUp($("#gsC"), G.coins * 10, 350, "$");
    await countUp($("#gsN"), G.near || 0, 300);
    counting = false;
    const r = rankOf(sc); $("#gRank").textContent = r; $("#gRank").className = "grank on r" + r;
    beep(r === "S" || r === "A" ? [523, 659, 784, 1046] : [392, 330], .1, "triangle", .05);
    if (isRec) $("#gRec").classList.add("on");
    if (pending) {
      $("#gWorld").textContent = "🌍 …";
      const wr = await pending; pending = null;
      $("#gWorld").textContent = wr ? "🌍 WORLD RANK #" + wr : "";
      if (wr) { $("#gWorld").classList.remove("on"); void $("#gWorld").offsetWidth; $("#gWorld").classList.add("on"); }
    }
    renderBoard();
  };
  const exit = () => { panel.classList.remove("on"); document.body.classList.remove("gaming", "playing", "fast"); clearInterval(timer); starting = false; $("#gcount").className = "gcount"; };
  const open = () => { scrollTo({top:0, behavior: reduce ? "auto" : "smooth"}); showPanel(false); beep([392, 523, 659], .08, "triangle"); };
  const start = () => {
    if (counting || starting) return;
    const nk = $("#gNick").value.replace(/[^A-Za-z0-9_ .-]/g, "").trim().slice(0, 16);
    if (nk.length >= 2) store.set("nick", nk);
    LB.start();
    panel.classList.remove("on"); document.body.classList.add("gaming", "playing");
    $("#gScore").textContent = "0"; $("#gCoins").textContent = "0"; $("#gPb").textContent = best ? "PB " + fmt(best) : "";
    pbShown = false; combo = 0; SC.game._rec = false;
    const c = $("#gcount"), seq = ["3", "2", "1", "GO!"];
    const go = () => {
      starting = false;
      SC.play(); clearInterval(timer);
      timer = setInterval(() => {
        const G = SC.game, s = SC.state ? SC.state() : {speed: G.speed, boostT: 0};
        $("#gScore").textContent = fmt(G.score);
        if (best === 0 && G.score > 0) G._rec = true;
        if (!pbShown && best > 0 && G.score > best) { pbShown = true; G._rec = true; pop("★ NEW RECORD ★", "rec"); flash("gold"); beep([784, 988, 1318], .08, "triangle", .05); }
        $("#skmh").textContent = Math.round(s.speed * 3.2);
        $("#sdial").style.setProperty("--v", Math.min(1, s.speed / 115).toFixed(3));
        $("#snos").style.width = (s.boostT > 0 ? s.boostT / 1.3 * 100 : 100) + "%";
        document.body.classList.toggle("fast", s.speed > 75 || s.boostT > 0);
        if (combo && Date.now() - comboT > 2200) combo = 0;
      }, 60);
    };
    if (reduce) { go(); return; }
    starting = true;
    let i = 0;
    const step = () => {
      if (!starting) return;
      c.textContent = seq[i]; c.className = "gcount"; void c.offsetWidth; c.className = "gcount on" + (i === 3 ? " go" : "");
      beep(i === 3 ? [784, 1046] : [440], i === 3 ? .18 : .12, "square", .05);
      if (i === 3) { go(); setTimeout(() => { c.className = "gcount"; }, 700); return; }
      i++; setTimeout(step, 650);
    };
    step();
  };
  SC.onGame(ev => {
    if (ev === "coin") {
      combo = Date.now() - comboT < 2200 ? combo + 1 : 1; comboT = Date.now();
      $("#gCoins").textContent = SC.game.coins; beep([988 + combo * 60, 1318 + combo * 60], .05, "square", .03);
      pop(combo > 1 ? `+$10  COMBO x${combo}` : "+$10", "cash");
    }
    if (ev === "near") { pop("⚡ NEAR MISS +50", "near"); beep([1568], .04, "sawtooth", .025); }
    if (ev === "crash") {
      clearInterval(timer); document.body.classList.remove("playing", "fast");
      const sc = Math.floor(SC.game.score); if (sc > best) { best = sc; store.set("best", best); }
      pending = LB.on ? LB.submit(nickname(), SC.game.score, SC.game.coins, SC.game.near || 0) : null;
      if (SC.game.coins) { st.cash += SC.game.coins * 10; st.xp += SC.game.coins * 2; save(); updateHud(); }
      beep([220, 165, 110], .18, "sawtooth", .06);
      flash("red");
      document.body.classList.add("shake"); setTimeout(() => document.body.classList.remove("shake"), 500);
      reward("game", tr("mGame"), tr("gScore") + " " + sc.toLocaleString("en"), 300, 100);
      setTimeout(() => showPanel(true), 750);
    }
    if (ev === "quit") exit();
  });
  $("#playTop").addEventListener("click", open);
  const ph = $("#playHero"); if (ph) ph.addEventListener("click", open);
  $("#gGo").addEventListener("click", start);
  $("#gBack").addEventListener("click", exit);
  $("#gQuit").addEventListener("click", () => SC.quit());
  addEventListener("keydown", e => {
    if (!panel.classList.contains("on")) return;
    if (e.key === "Escape") exit();
    else if ((e.key === "Enter" || (e.key === " " && document.activeElement !== $("#gNick"))) && document.activeElement !== $("#gBack")) { e.preventDefault(); start(); }
  });
}

/* ---------- walkthrough videos: YouTube player loads only when asked ---------- */
function bindVideos(){
  if (!$("[data-yt],[data-ytlist]")) return;
  document.body.insertAdjacentHTML("beforeend", `<div class="vmodal" id="vModal" role="dialog" aria-modal="true" aria-label="Walkthrough video"><div class="vbox"><button class="iconbtn vclose" id="vClose" aria-label="Close">✕</button><div class="vframe" id="vFrame"></div></div></div>`);
  const m = $("#vModal"), f = $("#vFrame");
  const close = () => { m.classList.remove("on"); f.innerHTML = ""; };
  document.addEventListener("click", e => {
    const b = e.target.closest("[data-yt],[data-ytlist]"); if (!b) return;
    e.preventDefault();
    const src = b.dataset.yt
      ? `https://www.youtube-nocookie.com/embed/${encodeURIComponent(b.dataset.yt)}?autoplay=1&rel=0&modestbranding=1${/^\d+$/.test(b.dataset.start || "") ? "&start=" + b.dataset.start : ""}`
      : `https://www.youtube-nocookie.com/embed/videoseries?list=${encodeURIComponent(b.dataset.ytlist)}&rel=0`;
    f.innerHTML = `<iframe src="${src}" title="GTA 6 walkthrough video" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>`;
    m.classList.add("on"); beep([523, 784], .06, "triangle");
  });
  $("#vClose").addEventListener("click", close);
  m.addEventListener("click", e => { if (e.target === m) close(); });
  addEventListener("keydown", e => { if (e.key === "Escape" && m.classList.contains("on")) close(); });
}

/* ---------- player login / profile (automatic, no password) ---------- */
function bindProfile(){
  const btn = $("#profBtn"); if (!btn) return;
  const ur = lang === "hi";
  const T = ur ? { title:"Tera Profile", on:"Logged in hai ✓", how:"Koi password nahi chahiye. Site tujhe khud login kar deti hai aur tera progress isi browser mein save rehta hai.", name:"Racer naam", save:"Save", saved:"Save ho gaya ✓", ticket:"Lucky draw ticket", best:"Best score", cash:"Cash", level:"Level", play:"🎮 Neon Run khel", warn:"Browser data clear kiya ya doosra phone/browser use kiya to naya profile banega.", gIn:"Google se login karo", gWhy:"Apna progress har phone aur browser pe saath rakho.", gOn:"Google se connected", gOut:"Logout" }
               : { title:"Your Profile", on:"Logged in ✓", how:"No password needed. The site signs you in automatically and keeps your progress in this browser.", name:"Racer name", save:"Save", saved:"Saved ✓", ticket:"Lucky draw ticket", best:"Best score", cash:"Cash", level:"Level", play:"🎮 Play Neon Run", warn:"Clearing browser data or switching device/browser starts a new profile.", gIn:"Sign in with Google", gWhy:"Keep your progress on every phone and browser.", gOn:"Connected with Google", gOut:"Log out" };
  document.body.insertAdjacentHTML("beforeend", `<div class="supmodal profmodal" id="profModal" role="dialog" aria-modal="true" aria-labelledby="profH"><div class="supbox">
    <div class="gtag">PLAYER</div>
    <div class="pfhead"><div class="cav sm" aria-hidden="true"><span id="pfInit">?</span><i>🎮</i></div><div><h2 id="profH">${esc(T.title)}</h2><div class="pfon">${esc(T.on)}</div></div></div>
    <p class="pfhow">${esc(T.how)}</p>
    <label class="pflabel" for="pfName">${esc(T.name)}</label>
    <div class="pfrow"><input id="pfName" maxlength="16" autocomplete="nickname" spellcheck="false"><button class="btn" id="pfSave">${esc(T.save)}</button></div>
    <div class="pfstats">
      <div><span>🎟 ${esc(T.ticket)}</span><b id="pfTicket">…</b></div>
      <div><span>🏆 ${esc(T.best)}</span><b id="pfBest">0</b></div>
      <div><span>💵 ${esc(T.cash)}</span><b id="pfCash">$0</b></div>
      <div><span>⭐ ${esc(T.level)}</span><b id="pfLvl">1</b></div>
    </div>
    <div class="pfgoogle" id="pfGoogle" hidden><button class="btn gbtn" id="pfG"><svg viewBox="0 0 48 48" width="18" height="18" aria-hidden="true"><path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z"/><path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/><path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-7.9l-6.5 5C9.5 39.6 16.2 44 24 44z"/><path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z"/></svg><span id="pfGTxt">${esc(T.gIn)}</span></button><p class="pfgnote" id="pfGNote">${esc(T.gWhy)}</p></div>
    <p class="note" id="pfWarn">${esc(T.warn)}</p>
    <div class="gbtns"><button class="btn primary" id="pfPlay">${esc(T.play)}</button><button class="btn" id="pfClose">✕</button></div>
  </div></div>`);
  const m = $("#profModal");
  const fill = async () => {
    const nk = nickname();
    $("#pfName").value = nk; $("#pfInit").textContent = nk.replace(/[^A-Za-z0-9]/g, "").slice(0, 2).toUpperCase() || "P";
    $("#pfBest").textContent = Number(store.get("best", 0)).toLocaleString("en");
    $("#pfCash").textContent = "$" + st.cash.toLocaleString("en"); $("#pfLvl").textContent = level();
    $("#profTxt").textContent = nk.slice(0, 10);
    if (LB.on) { await LB.init(); $("#pfTicket").textContent = LB.ticket() || "—"; } else $("#pfTicket").textContent = "—";
    if (GOOGLE_LOGIN && LB.on) {
      const a = await LB.account(); $("#pfGoogle").hidden = false;
      if (a && !a.anon) { $("#pfGTxt").textContent = T.gOut; $("#pfGNote").textContent = "✓ " + T.gOn + (a.email ? " · " + a.email : ""); $("#pfWarn").hidden = true; $("#pfG").dataset.mode = "out"; }
      else { $("#pfGTxt").textContent = T.gIn; $("#pfGNote").textContent = T.gWhy; $("#pfWarn").hidden = false; $("#pfG").dataset.mode = "in"; }
      $("#pfTicket").textContent = LB.ticket() || "—";
    }
  };
  const open = () => { fill(); m.classList.add("on"); beep([523, 659], .07, "triangle"); };
  const close = () => m.classList.remove("on");
  btn.addEventListener("click", open);
  $("#pfClose").addEventListener("click", close);
  m.addEventListener("click", e => { if (e.target === m) close(); });
  addEventListener("keydown", e => { if (e.key === "Escape" && m.classList.contains("on")) close(); });
  $("#pfSave").addEventListener("click", () => {
    const v = $("#pfName").value.replace(/[^A-Za-z0-9_ .-]/g, "").trim().slice(0, 16);
    if (v.length >= 2) { store.set("nick", v); const g = $("#gNick"); if (g) g.value = v; $("#pfSave").textContent = T.saved; setTimeout(() => $("#pfSave").textContent = T.save, 1500); fill(); beep([988, 1318], .05, "square", .03); }
  });
  $("#pfPlay").addEventListener("click", () => { close(); const pt = $("#playTop"); if (pt) pt.click(); });
  $("#pfG").addEventListener("click", () => { $("#pfG").dataset.mode === "out" ? LB.logout() : LB.google(); });
  $("#profTxt").textContent = (store.get("nick", "") || "LOGIN").slice(0, 10);
  if (LB.on) setTimeout(() => LB.init(), 2500);   // sign the visitor in quietly so the ticket exists
}



/* ---------- monetization: ads + "where to buy" (inactive until MONEY is filled in) ---------- */
function bindMoney(){
  const slots = $$(".ad");
  const hideSlots = () => slots.forEach(el => { el.hidden = true; el.style.display = "none"; });
  if (!MONEY.adsense || MONEY.noAdPages.includes(PAGE)) hideSlots();
  else {
    const sc = document.createElement("script"); sc.async = true; sc.crossOrigin = "anonymous";
    sc.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + encodeURIComponent(MONEY.adsense);
    document.head.appendChild(sc);
    if (MONEY.adsenseSlot) slots.forEach(el => { el.className = "adslot"; el.innerHTML = `<ins class="adsbygoogle" style="display:block" data-ad-client="${esc(MONEY.adsense)}" data-ad-slot="${esc(MONEY.adsenseSlot)}" data-ad-format="auto" data-full-width-responsive="true"></ins>`; try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch(e) {} });
    else hideSlots();   // auto ads place themselves
  }
  const links = [["Eneba", MONEY.eneba, "Digital key deals"], ["Amazon", MONEY.amazon, "Disc & console bundles"]].filter(l => l[1]);
  if (!links.length || (!["price", "countries", "pc", "home"].includes(PAGE) && !document.body.dataset.country)) return;
  const main = $("main"); if (!main) return;
  main.insertAdjacentHTML("beforeend", `<section class="glass buybox reveal in"><h3>🛒 Where to buy GTA 6</h3><div class="buybtns">${links.map(([n, u, d]) => `<a class="btn primary" href="${esc(u)}" target="_blank" rel="noopener sponsored">${esc(n)}<small>${esc(d)}</small></a>`).join("")}</div><p class="note">Affiliate links: GamerBhai may earn a small commission at no extra cost to you. Only buy from official or trusted stores; avoid "free GTA 6" offers.</p></section>`);
}

/* ---------- share bar (free promotion: every visitor can spread the site) ---------- */
function bindShare(){
  const main = $("main"); if (!main || PAGE === "game") return;
  const url = "https://gamerbhai.com" + location.pathname.replace(/\.html$/, "").replace(/\/index$/, "/");
  const title = document.title.replace(/\s*[|–-]\s*(GamerBhai|GTA 6 Guide).*$/, "");
  const msg = `${title} 🔥 GTA 6 guides, cheats, map + free mini-game with a $100 lucky draw:`;
  const e = encodeURIComponent, u = e(url), m = e(msg);
  const L = [
    ["WhatsApp", "🟢", `https://wa.me/?text=${m}%20${u}`],
    ["Telegram", "✈️", `https://t.me/share/url?url=${u}&text=${m}`],
    ["X", "𝕏", `https://x.com/intent/post?text=${m}&url=${u}`],
    ["Facebook", "📘", `https://www.facebook.com/sharer/sharer.php?u=${u}`],
    ["Reddit", "👽", `https://www.reddit.com/submit?url=${u}&title=${e(title)}`]
  ];
  main.insertAdjacentHTML("beforeend", `<section class="sharebar glass reveal in"><div><b>📣 Share GamerBhai</b><p>Every new player brings the <a href="contest.html#draw">$100 lucky draw</a> closer.</p></div><div class="sharebtns">${navigator.share ? `<button class="shb" id="shNative">📤 Share</button>` : ""}${L.map(([n, i, h]) => `<a class="shb" href="${h}" target="_blank" rel="noopener nofollow">${i} ${n}</a>`).join("")}<button class="shb" id="shCopy">🔗 Copy link</button><a class="shb" href="https://www.youtube.com/@gamerbhaicom?sub_confirmation=1" target="_blank" rel="noopener">▶ Subscribe</a></div></section>`);
  const nat = $("#shNative"); if (nat) nat.addEventListener("click", () => navigator.share({ title, text: msg, url }).catch(() => {}));
  $("#shCopy").addEventListener("click", async () => { try { await navigator.clipboard.writeText(url); $("#shCopy").textContent = "✓ Copied"; } catch(_) { prompt("Copy this link:", url); } setTimeout(() => $("#shCopy").textContent = "🔗 Copy link", 1600); });
}


/* ---------- English-only guide pages: offer a machine-translated read ---------- */
function transBar(){
  const old = $("#trBar"); if (old) old.remove();
  if (!["story","walkthrough","guides","contest"].includes(PAGE) || lang === "en" || !/gamerbhai\.com$/.test(location.hostname)) return;
  const cc = store.get("cc", "");
  const tl = { hi: cc === "IN" ? "hi" : "ur", zh: "zh-CN", es: "es", ar: "ar", pt: "pt", id: "id", fr: "fr", ru: "ru", de: "de", ja: "ja" }[lang]; if (!tl) return;
  const name = (LANGS.find(l => l.code === lang) || {}).name || lang;
  const href = `https://gamerbhai-com.translate.goog${location.pathname}?_x_tr_sl=en&_x_tr_tl=${tl}&_x_tr_hl=${tl}`;
  const txt = { hi: "Ye page abhi English mein hai.", zh: "此页面目前只有英文版。", es: "Esta página solo está en inglés.", ar: "هذه الصفحة بالإنجليزية فقط حالياً.", pt: "Esta página está só em inglês.", id: "Halaman ini masih berbahasa Inggris.", fr: "Cette page est seulement en anglais.", ru: "Эта страница пока только на английском.", de: "Diese Seite ist nur auf Englisch.", ja: "このページは現在英語のみです。" }[lang];
  const go = { hi: "Urdu/Hindi mein parho", zh: "用中文阅读", es: "Leer en español", ar: "اقرأها بالعربية", pt: "Ler em português", id: "Baca dalam Bahasa Indonesia", fr: "Lire en français", ru: "Читать на русском", de: "Auf Deutsch lesen", ja: "日本語で読む" }[lang];
  const main = $("main"); if (!main) return;
  main.insertAdjacentHTML("afterbegin", `<div class="trbar glass" id="trBar"><span>🌐 ${esc(txt)}</span><a class="btn" href="${href}" rel="nofollow">${esc(go)} → ${esc(name)}</a></div>`);
}

/* ---------- community: posts, comments, live chat, uploads with approval ---------- */
function bindCommunity(){
  if (!$("#cm")) return;
  const msg = (t, bad) => { const m = $("#cmMsg"); m.textContent = t || ""; m.classList.toggle("bad", !!bad); };
  const ago = d => { const s = (Date.now() - new Date(d)) / 1000; return s < 60 ? "just now" : s < 3600 ? Math.floor(s / 60) + "m ago" : s < 86400 ? Math.floor(s / 3600) + "h ago" : new Date(d).toLocaleDateString(); };
  const txt = s => esc(s).replace(/\n/g, "<br>");
  const author = () => nickname().replace(/[^A-Za-z0-9_ .-]/g, "").slice(0, 16).padEnd(2, "_");
  let sb, me = null, admin = false, real = false, file = null, chatTimer = null, lastChat = 0;

  $$(".cmtabs button").forEach(b => b.addEventListener("click", () => {
    $$(".cmtabs button").forEach(x => x.classList.toggle("on", x === b));
    $$(".cmpane").forEach(x => x.classList.toggle("on", x.id === "cm" + b.dataset.tab[0].toUpperCase() + b.dataset.tab.slice(1)));
    if (b.dataset.tab === "chat") loadChat(true);
    if (b.dataset.tab === "review") loadQueue();
  }));

  async function urls(rows){
    const paths = rows.filter(r => r.file_path).map(r => r.file_path); if (!paths.length) return {};
    const { data } = await sb.storage.from("community").createSignedUrls(paths, 3600);
    const o = {}; (data || []).forEach(d => { if (d.signedUrl) o[d.path] = d.signedUrl; }); return o;
  }
  function card(p, u, queue){
    const mine = me && p.user_id === me, canDel = mine || admin;
    const badge = p.status === "pending" ? `<span class="cmbadge rev">⏳ Under review${queue ? "" : " · only you and moderators can see this"}</span>` : p.status === "rejected" ? `<span class="cmbadge rej">✕ Not approved</span>` : "";
    return `<article class="glass cmpost${p.status !== "approved" ? " pending" : ""}" data-id="${p.id}">
      <div class="cmhead"><div class="cav sm" aria-hidden="true"><span>${esc(p.author.slice(0, 2).toUpperCase())}</span></div><div><b>${esc(p.author)}</b><small>${ago(p.created_at)}</small></div>${badge}</div>
      <p class="cmtext">${txt(p.body)}</p>
      ${p.file_path ? (u[p.file_path] ? `<a href="${esc(u[p.file_path])}" target="_blank" rel="noopener"><img class="cmimg" src="${esc(u[p.file_path])}" alt="Image posted by ${esc(p.author)}" loading="lazy"></a>` : `<div class="cmimg ph">🖼️ Image</div>`) : ""}
      <div class="cmacts">
        ${p.status === "approved" && !queue ? `<button class="cmlink" data-cm="${p.id}">💬 Comments</button>` : ""}
        ${admin && p.status !== "approved" ? `<button class="cmlink ok" data-approve="${p.id}">✓ Approve</button>` : ""}
        ${admin && p.status === "pending" ? `<button class="cmlink no" data-reject="${p.id}">✕ Reject</button>` : ""}
        ${canDel ? `<button class="cmlink no" data-delpost="${p.id}" data-file="${esc(p.file_path || "")}">🗑 Delete</button>` : ""}
      </div>
      <div class="cmcomments" id="cmc${p.id}" hidden></div>
    </article>`;
  }
  async function loadPosts(){
    const { data, error } = await sb.from("posts").select("*").order("created_at", { ascending: false }).limit(40);
    if (error) { $("#cmPosts").innerHTML = `<p class="note">Couldn't load posts. Try again in a minute.</p>`; return; }
    const rows = (data || []).filter(p => p.status === "approved" || p.user_id === me);
    const u = await urls(rows);
    $("#cmPosts").innerHTML = rows.length ? rows.map(p => card(p, u)).join("") : `<div class="glass"><p>No posts yet. Be the first! 🔥</p></div>`;
    if (admin) { const n = (data || []).filter(p => p.status === "pending").length; $("#cmPendN").textContent = n; }
  }
  async function loadQueue(){
    if (!admin) return;
    const { data } = await sb.from("posts").select("*").eq("status", "pending").order("created_at");
    const u = await urls(data || []);
    $("#cmPendN").textContent = (data || []).length;
    $("#cmQueue").innerHTML = (data || []).length ? data.map(p => card(p, u, true)).join("") : `<div class="glass"><p>✅ Nothing waiting for review.</p></div>`;
  }
  async function loadComments(id){
    const box = $("#cmc" + id);
    const { data } = await sb.from("comments").select("*").eq("post_id", id).order("created_at").limit(100);
    box.innerHTML = (data || []).map(c => `<div class="cmcom"><b>${esc(c.author)}</b> <small>${ago(c.created_at)}</small>${(me && c.user_id === me) || admin ? ` <button class="cmlink no" data-delcom="${c.id}" data-post="${id}">🗑</button>` : ""}<p>${txt(c.body)}</p></div>`).join("")
      + `<div class="cmrow"><input maxlength="500" placeholder="Write a comment…" data-cin="${id}"><button class="btn" data-csend="${id}">Send</button></div>`;
  }
  async function loadChat(start){
    const { data } = await sb.from("chat").select("*").order("created_at", { ascending: false }).limit(60);
    const log = $("#cmChatLog"), stick = log.scrollTop + log.clientHeight >= log.scrollHeight - 30;
    const rows = (data || []).reverse(), last = rows.length ? rows[rows.length - 1].id : 0;
    if (last !== lastChat || start) {
      log.innerHTML = rows.length ? rows.map(m => `<div class="cmmsgline${me && m.user_id === me ? " me" : ""}"><b>${esc(m.author)}</b><span>${txt(m.body)}</span><small>${ago(m.created_at)}</small>${admin || (me && m.user_id === me) ? `<button class="cmlink no" data-delchat="${m.id}">🗑</button>` : ""}</div>`).join("") : `<p class="note">No messages yet. Say hi 👋</p>`;
      if (stick || start) log.scrollTop = log.scrollHeight;
      lastChat = last;
    }
    if (!chatTimer) chatTimer = setInterval(() => { if (!document.hidden && $("#cmChat").classList.contains("on")) loadChat(); }, 4000);
  }
  const err = e => (e && e.message || "").replace(/^.*?(Slow down.*)$/, "$1") || "Something went wrong.";

  document.addEventListener("click", async e => {
    const b = e.target.closest("[data-cm],[data-approve],[data-reject],[data-delpost],[data-delcom],[data-csend],[data-delchat]"); if (!b || !sb) return;
    const d = b.dataset;
    if (d.cm) { const box = $("#cmc" + d.cm); box.hidden = !box.hidden; if (!box.hidden) loadComments(d.cm); }
    else if (d.approve) { await sb.from("posts").update({ status: "approved" }).eq("id", d.approve); loadQueue(); loadPosts(); }
    else if (d.reject) { const p = b.closest(".cmpost"); const f = p && p.querySelector("[data-file]"); if (f && f.dataset.file) await sb.storage.from("community").remove([f.dataset.file]); await sb.from("posts").update({ status: "rejected" }).eq("id", d.reject); loadQueue(); loadPosts(); }
    else if (d.delpost !== undefined) { if (!b.dataset.sure) { b.dataset.sure = 1; b.textContent = "Tap again to delete"; return; } if (d.file) await sb.storage.from("community").remove([d.file]); await sb.from("posts").delete().eq("id", d.delpost); loadPosts(); if (admin) loadQueue(); }
    else if (d.delcom) { await sb.from("comments").delete().eq("id", d.delcom); loadComments(d.post); }
    else if (d.delchat) { await sb.from("chat").delete().eq("id", d.delchat); lastChat = -1; loadChat(); }
    else if (d.csend) {
      const i = $(`[data-cin="${d.csend}"]`), v = i.value.trim(); if (!v) return;
      b.disabled = true; const { error } = await sb.from("comments").insert({ post_id: Number(d.csend), author: author(), body: v }); b.disabled = false;
      if (error) { i.value = ""; i.placeholder = err(error); } else { loadComments(d.csend); beep([784, 988], .05, "triangle"); }
    }
  });
  document.addEventListener("keydown", e => { if (e.key === "Enter" && e.target.dataset && e.target.dataset.cin) { const s = $(`[data-csend="${e.target.dataset.cin}"]`); if (s) s.click(); } });

  $("#cmFile").addEventListener("change", e => {
    const f = e.target.files[0]; file = null; $("#cmFname").textContent = "";
    if (!f) return;
    if (!/^image\/(jpeg|png|webp|gif)$/.test(f.type)) { msg("Only JPG, PNG, WEBP or GIF images.", true); return; }
    if (f.size > 5 * 1024 * 1024) { msg("That image is over 5 MB.", true); return; }
    file = f; $("#cmFname").textContent = "📎 " + f.name; msg("");
  });
  $("#cmPost").addEventListener("click", async () => {
    const body = $("#cmBody").value.trim();
    if (!body) { msg("Write something first.", true); return; }
    $("#cmPost").disabled = true; msg(file ? "Uploading…" : "Posting…");
    let path = null;
    if (file) {
      path = `${me}/${Date.now()}-${Math.random().toString(36).slice(2, 8)}.${(file.type.split("/")[1] || "jpg").replace("jpeg", "jpg")}`;
      const up = await sb.storage.from("community").upload(path, file, { contentType: file.type, upsert: false });
      if (up.error) { msg("Upload failed: " + err(up.error), true); $("#cmPost").disabled = false; return; }
    }
    const { error } = await sb.from("posts").insert({ author: author(), body, file_path: path, file_type: file ? file.type : null });
    $("#cmPost").disabled = false;
    if (error) { if (path) sb.storage.from("community").remove([path]); msg(err(error), true); return; }
    $("#cmBody").value = ""; $("#cmFile").value = ""; $("#cmFname").textContent = "";
    msg(file && !admin ? "✓ Sent! Your image is ⏳ under review. It goes public once a moderator approves it." : "✓ Posted!");
    file = null; beep([523, 659, 784], .06, "triangle"); loadPosts();
  });
  $("#cmChatSend").addEventListener("click", async () => {
    const i = $("#cmChatIn"), v = i.value.trim(); if (!v || !sb) return;
    $("#cmChatSend").disabled = true; const { error } = await sb.from("chat").insert({ author: author(), body: v }); $("#cmChatSend").disabled = false;
    if (error) { i.placeholder = err(error); return; }
    i.value = ""; i.placeholder = "Say something…"; loadChat();
  });
  $("#cmChatIn").addEventListener("keydown", e => { if (e.key === "Enter") $("#cmChatSend").click(); });
  $("#cmLogin").addEventListener("click", () => LB.google());

  (async () => {
    if (!LB.on || !(await LB.init())) { $("#cmPosts").innerHTML = `<p class="note">Community is offline right now.</p>`; return; }
    sb = LB.sb;
    const a = await LB.account(); me = LB.uid; real = !!(a && !a.anon);
    const r = await sb.rpc("is_admin"); admin = !r.error && r.data === true;
    $("#cmReviewTab").hidden = !admin;
    $("#cmNeedLogin").hidden = real || !GOOGLE_LOGIN; $("#cmForm").hidden = !real;
    loadPosts();
  })();
}

/* ---------- $100 lucky draw at 50,000 members ---------- */
const DRAW = { goal: 50000, prize: "$100" };
function bindDraw(){
  // home page: compact progress banner under the hero; contest page has the full section
  const ctas = $(".hero .ctas");
  if (ctas) ctas.insertAdjacentHTML("afterend", `<a class="drawmini" href="contest#draw"><b>💵 ${DRAW.prize} LUCKY DRAW</b><span class="dbar"><i class="dfill"></i></span><em class="dcount">… / ${DRAW.goal.toLocaleString("en")} members</em></a>`);
  const bars = $$(".dfill"), counts = $$(".dcount");
  if (!bars.length) return;
  const paint = n => {
    const pct = Math.min(100, n / DRAW.goal * 100);
    bars.forEach(b => b.style.width = Math.max(pct, 1.5) + "%");
    counts.forEach(c => c.textContent = `${n.toLocaleString("en")} / ${DRAW.goal.toLocaleString("en")} members`);
    const left = $("#dLeft"); if (left) left.textContent = Math.max(0, DRAW.goal - n).toLocaleString("en");
    const pc = $("#dPct"); if (pc) pc.textContent = pct.toFixed(pct < 1 ? 2 : 1) + "%";
  };
  const load = async () => {
    const n = await LB.members(); if (n == null) return;
    paint(n);
    const t = LB.ticket(), tk = $("#dTicket");
    if (tk) tk.textContent = t || "play 1 game to get yours";
  };
  load(); setInterval(load, 60000);
}

/* ---------- Neon Run Season 1 contest ---------- */
// Fill these in, set live:true, then also remove the noindex line in contest.html and add /contest to sitemap.xml.
const CONTEST = {
  live: true,
  prize: "",            // secret until PC release day: page shows "Mystery gift"
  value: "revealed on GTA 6 PC release day",
  minAge: 13,
  countries: "all countries where this contest is legal",
  contact: "",          // posted on this page on PC release day (claim instructions)
  start: "2026-11-23"
};
function bindContest(){
  if (CONTEST.live) {
    const box = $("#gpanel .gbox");
    if (box) box.insertAdjacentHTML("beforeend", `<a class="cbanner" href="contest">🏆 Season 1 is live: #1 wins ${esc(CONTEST.prize || "a mystery gift")} →</a>`);
  }
  if (PAGE !== "contest") return;
  $$("[data-c]").forEach(el => { const v = CONTEST[el.dataset.c]; if (v !== "" && v != null) el.textContent = el.dataset.c === "start" ? fmtDate(v) : v; });
  if (!CONTEST.live) $("#cPreview").hidden = false;
  if (CONTEST.start) $("#cDays").textContent = Math.max(0, Math.floor((Date.now() - new Date(CONTEST.start + "T00:00:00Z")) / 864e5));
  $("#cPlay").addEventListener("click", () => { const p = $("#playTop"); if (p) p.click(); });
  const list = $("#cList");
  const load = async () => {
    const rows = await LB.top(10);
    if (!rows) { list.innerHTML = `<li class="muted">Leaderboard offline. Try again soon.</li>`; return; }
    list.innerHTML = rows.length
      ? rows.map(r => `<li class="${r.me ? "me" : ""}"><span class="lr">${r.rank === 1 ? "👑" : r.rank}</span><span class="ln">${esc(r.name)}</span><b>${Number(r.score).toLocaleString("en")}</b></li>`).join("")
      : `<li class="muted">No scores yet. Be the first! 🏁</li>`;
  };
  load(); setInterval(load, 30000);
}

/* ---------- support / donation ---------- */
const SUPPORT_URL = "";   // optional: Patreon (or other) page link
// crypto wallets: one entry per coin/network, e.g. { coin:"USDT", net:"TRON (TRC20)", addr:"T..." }
// all addresses read from the owner's Binance deposit pages; none of these networks needs a memo/tag
const CRYPTO = [
  { coin:"USDT", icon:"₮", net:"BNB Smart Chain (BEP20)", addr:"0x3a39552f276f29ba3e9b0b627544f607c88dbf51" },
  { coin:"USDT", icon:"₮", net:"TRON (TRC20)",            addr:"TEndW6gsMJGqHLWcXTuJV9S1wcPeVx2Zu5" },
  { coin:"BTC",  icon:"₿", net:"Bitcoin",                 addr:"16KyPrLGwVrGYDV3rDZ81ZQKdrVMw2BCPj" },
  { coin:"ETH",  icon:"Ξ", net:"Ethereum (ERC20)",        addr:"0x3a39552f276f29ba3e9b0b627544f607c88dbf51" },
  { coin:"SOL",  icon:"◎", net:"Solana",                  addr:"FzM2QzUXKAw9DsjniwGLwJ3mdrEZDFTwEsrArFEDCaf8" },
  { coin:"LTC",  icon:"Ł", net:"Litecoin",                addr:"LPrqW8w3pgK4pqRe1X9Pib1hyMfcBEZaFD" },
  { coin:"DOGE", icon:"Ð", net:"Dogecoin",                addr:"DRYJgttWDgc4rekvHvtfudtX7a47fea62k" },
  { coin:"TRX",  icon:"◈", net:"TRON (TRC20)",            addr:"TEndW6gsMJGqHLWcXTuJV9S1wcPeVx2Zu5" }
];
function bindSupport(){
  const hasUrl = /^https:\/\//.test(SUPPORT_URL);
  const wallets = CRYPTO.filter(w => w && /^[A-Za-z0-9]{20,100}$/.test(w.addr || ""));
  if (!hasUrl && !wallets.length) return;
  const ur = lang === "hi";
  const T = ur ? {
    tag: "SIDE MISSION", h: "Site ko free rakho", p: "Ye site ek banda akela chala raha hai. Koi paywall nahi, koi login nahi. Agar site ne help ki ya game mein maza aaya, to chhota sa support bhi bohat bara hai. 💜",
    b: "☕ Support karo ↗", x: "Abhi nahi", open: "☕ Support karo", crypto: "Crypto se support", copy: "Copy", copied: "Copy ho gaya ✓",
    warn: "Sirf isi network pe bhejna. Ghalat network = paise gum."
  } : {
    tag: "SIDE MISSION", h: "Keep the site free", p: "This site is made by one person. No paywall, no sign-up. If it helped you or Neon Run made your day, a small tip keeps it running. 💜",
    b: "☕ Support ↗", x: "Not now", open: "☕ Support", crypto: "Support with crypto", copy: "Copy", copied: "Copied ✓",
    warn: "Send only on this network. Wrong network = lost funds."
  };
  const walletHtml = wallets.length ? `<div class="supcrypto"><div class="supch">🪙 ${esc(T.crypto)}</div>
      <div class="wtabs" role="tablist">${wallets.map((w, i) => `<button class="wtab${i ? "" : " on"}" role="tab" data-i="${i}" aria-selected="${!i}"><i>${esc(w.icon || "●")}</i>${esc(w.coin)}<small>${esc((w.net.match(/\(([^)]+)\)/) || [, w.net])[1])}</small></button>`).join("")}</div>
      <div class="wpanel"><div class="wqr" id="wQr" aria-label="QR code"></div>
        <div class="wbody"><div class="wtop"><b id="wCoin"></b><span id="wNet"></span></div>
        <div class="wrow"><code id="wAddr"></code></div><button class="btn wcopy" id="wCopy">${esc(T.copy)}</button></div></div>
      <p class="wwarn">⚠️ ${esc(T.warn)}</p></div>` : "";
  document.body.insertAdjacentHTML("beforeend", `<div class="supmodal" id="supModal" role="dialog" aria-modal="true" aria-labelledby="supH"><div class="supbox">
    <div class="gtag">${T.tag}</div><h2 id="supH">${esc(T.h)}</h2><p>${esc(T.p)}</p>
    <div class="supperks"><span>⚡ Faster updates</span><span>🎮 More games</span><span>🌍 More countries</span></div>
    ${walletHtml}
    <div class="gbtns">${hasUrl ? `<a class="btn primary" id="supGo" href="${esc(SUPPORT_URL)}" target="_blank" rel="noopener">${esc(T.b)}</a>` : ""}<button class="btn" id="supX">${esc(T.x)}</button></div>
  </div></div>`);
  const m = $("#supModal");
  const thanks = () => reward("support", "THANK YOU 💜", ur ? "Shukriya yaar!" : "You're a legend!", 0, 0);
  const open = () => { m.classList.add("on"); beep([523, 659, 784], .08, "triangle"); setTimeout(() => ($("#supGo") || $(".wcopy") || $("#supX")).focus(), 50); };
  const close = () => m.classList.remove("on");
  $("#supX").addEventListener("click", close);
  m.addEventListener("click", e => { if (e.target === m) close(); });
  addEventListener("keydown", e => { if (e.key === "Escape" && m.classList.contains("on")) close(); });
  if (hasUrl) $("#supGo").addEventListener("click", () => { close(); thanks(); });
  let cur = 0;
  const drawQr = () => {
    const box = $("#wQr"); if (!box) return;
    if (!window.qrcode) { box.textContent = "QR…"; return; }
    const q = qrcode(0, "M"); q.addData(wallets[cur].addr); q.make();
    box.innerHTML = q.createSvgTag({ cellSize: 4, margin: 2, scalable: true });
  };
  const showWallet = i => {
    if (!wallets.length) return;
    cur = i; const w = wallets[i];
    $("#wCoin").textContent = w.coin; $("#wNet").textContent = w.net; $("#wAddr").textContent = w.addr;
    $$(".wtab").forEach(t => { const on = +t.dataset.i === i; t.classList.toggle("on", on); t.setAttribute("aria-selected", on); });
    drawQr();
  };
  if (wallets.length) {
    showWallet(0);
    if (!window.qrcode) { const s = document.createElement("script"); s.src = "https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js"; s.onload = drawQr; document.head.appendChild(s); }
    $$(".wtab").forEach(t => t.addEventListener("click", () => { showWallet(+t.dataset.i); beep([700 + 40 * +t.dataset.i], .04, "square", .02); }));
    $("#wCopy").addEventListener("click", async () => {
      const b = $("#wCopy"), addr = wallets[cur].addr;
      try { await navigator.clipboard.writeText(addr); }
      catch(e) { const r = document.createRange(); r.selectNodeContents($("#wAddr")); const s = getSelection(); s.removeAllRanges(); s.addRange(r); document.execCommand("copy"); }
      b.textContent = T.copied; b.classList.add("ok"); beep([988, 1318], .05, "square", .03); thanks();
      setTimeout(() => { b.textContent = T.copy; b.classList.remove("ok"); }, 2000);
    });
  }
  [$("#supFoot"), $("#gSup")].forEach(b => { if (b) { b.hidden = false; b.addEventListener("click", open); } });
  if (PAGE === "about") {
    const sec = $$("main section")[1];
    const html = `<section class="reveal in"><div class="glass supcard"><h2>☕ ${esc(T.h)}</h2><p>${esc(T.p)}</p><button class="btn primary" id="supAbout">${esc(T.open)}</button></div></section>`;
    if (sec) sec.insertAdjacentHTML("beforebegin", html); else $("main").insertAdjacentHTML("beforeend", html);
    $("#supAbout").addEventListener("click", open);
  }
}

/* ---------- boot ---------- */
buildChrome();
bindGame();
applyText();
arriveIn();
hudLoop();
bindSupport();
bindContest();
bindVideos();
bindDraw();
bindProfile();
bindCommunity();
bindMoney();
bindShare();
transBar();
if ("serviceWorker" in navigator && location.protocol === "https:") { const regSW = () => navigator.serviceWorker.register("/sw.js").catch(() => {}); document.readyState === "complete" ? setTimeout(regSW, 1500) : addEventListener("load", regSW); }
document.addEventListener("click", e => { const f = e.target.closest(".cphoto"); if (f) f.classList.toggle("on"); });
/* confirm the visitor's country with Cloudflare (same site, no extra service) */
if (!store.get("cc", null) && /gamerbhai\.com$/.test(location.hostname)) {
  fetch("/cdn-cgi/trace", { cache: "no-store" }).then(r => r.ok ? r.text() : "").then(t => {
    const cc = (t.match(/^loc=([A-Z]{2})$/m) || [])[1]; if (!cc) return;
    store.set("cc", cc);
    if (store.get("lang", null)) return;                    // visitor already chose a language
    const want = CC_LANG[cc];
    if (want && T[want] && want !== lang) { lang = want; $("#langSel").value = lang; applyText(); renderPage(); transBar(); }
  }).catch(() => {});
}
if (PAGE === "price") bindPrice();
renderPage();
const page = PAGES.find(p => p.id === PAGE);
if (page) setTimeout(() => reward("visit-" + PAGE, tr("mArea"), tr(page.nav), 250, 50), 600);
else if (PAGE === "country") setTimeout(() => { if (reward("visit-c-" + document.body.dataset.cur, tr("mArea"), document.body.dataset.country, 100, 30)) store.set("cur", document.body.dataset.cur); }, 600);

const _boost = window.SCENE.boost;
window.SCENE.boost = function(){ _boost && _boost(); const n = Date.now(); if (n - lastBoost > 4000) { lastBoost = n; st.cash += 5; save(); updateHud(); } };
})();
