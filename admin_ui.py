"""Every Fit · 파일럿 관리자 HTML (브랜드·탭·기간·진단 상세)."""

ADMIN_HTML = r"""<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css"/>
<title>Every Fit · 관리자</title>
<style>
:root{--brand:#e03d5c;--brand-soft:#fff1f4;--border:#e5e5ea;--text:#1c1c1e;--muted:#6b7280;--bg:#f2f2f7;--card:#fff;--pink:var(--brand)}
*{box-sizing:border-box}
body{margin:0;font-family:"Pretendard",system-ui,sans-serif;background:var(--bg);color:var(--text);font-size:14px;line-height:1.5}
.shell{max-width:1240px;margin:0 auto;padding:16px 20px 48px}
h1{font-size:20px;margin:0 0 4px;font-weight:700}
.sub{color:var(--muted);font-size:13px;margin:0 0 16px}
.toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;margin:0 0 16px;padding:14px;background:var(--card);border:1px solid var(--border);border-radius:14px}
.toolbar label{font-size:12px;color:var(--muted);display:flex;flex-direction:column;gap:4px}
.toolbar input,.toolbar select{padding:8px 10px;border:1px solid var(--border);border-radius:10px;font-size:13px}
.btn{padding:8px 14px;border-radius:10px;border:0;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit}
.btn-primary{background:var(--brand);color:#fff}
.btn-ghost{background:#fff;border:1px solid var(--border);color:var(--text)}
.tabs{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 16px}
.tabs button{padding:10px 16px;border-radius:999px;border:1px solid var(--border);background:#fff;cursor:pointer;font-weight:600;font-family:inherit}
.tabs button.on{background:var(--brand-soft);border-color:var(--brand);color:var(--brand)}
.panel{display:none}
.panel.on{display:block}
#admin-loading{margin:12px 0;padding:14px;border-radius:10px;background:var(--brand-soft);color:var(--brand);font-size:14px}
#admin-meta{margin:0 0 16px;padding:12px 14px;border-radius:12px;background:var(--card);border:1px solid var(--border);font-size:12px;color:var(--muted)}
#admin-meta.warn{background:#fffbeb;border-color:#fcd34d}
#admin-err{margin:0 0 12px;padding:12px;border-radius:10px;background:#fef2f2;color:#991b1b;font-size:14px;display:none}
.cards{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 16px}
.cards.loading{opacity:.45;pointer-events:none}
.card{background:var(--card);padding:12px 16px;border-radius:12px;border:1px solid var(--border);min-width:110px;flex:1 1 110px;max-width:200px}
.card b{display:block;font-size:22px;font-weight:700;color:var(--text)}
.card small{display:block;font-size:11px;color:var(--muted);margin-top:4px}
.card .pct{font-size:15px;font-weight:700;color:var(--brand)}
h2{font-size:16px;margin:20px 0 10px;font-weight:700}
h2:first-child{margin-top:0}
.table-wrap{overflow-x:auto;margin:0 0 16px;border-radius:12px;border:1px solid var(--border);background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:13px;min-width:720px}
th,td{border-bottom:1px solid var(--border);padding:8px 10px;text-align:left;vertical-align:top}
th{background:#fafafa;font-weight:600;font-size:12px}
input.inp,select.inp,textarea.inp{padding:6px 8px;border:1px solid var(--border);border-radius:8px;font-size:12px;font-family:inherit;width:100%}
textarea.inp{min-height:44px;resize:vertical}
.bar-chart{margin:12px 0 20px}
.bar-row{display:flex;align-items:center;gap:8px;margin:0 0 6px;font-size:12px}
.bar-row span.lbl{flex:0 0 72px;text-align:right;color:var(--muted)}
.bar-row span.track{flex:1;height:10px;background:#ececf0;border-radius:6px;overflow:hidden}
.bar-row span.fill{display:block;height:100%;background:var(--brand);border-radius:6px}
.bar-row span.val{flex:0 0 36px;font-weight:600}
.trend{margin:8px 0 16px}
.trend .bar-row span.lbl{flex:0 0 88px;text-align:left;font-size:11px}
#dx-detail{display:none;margin:0 0 20px;padding:16px;background:var(--card);border:1px solid var(--border);border-radius:14px}
#dx-detail h3{margin:0 0 12px;font-size:16px;color:var(--brand)}
.dx-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:900px){.dx-grid{grid-template-columns:1fr}}
.dx-block{font-size:13px;line-height:1.55}
.dx-block pre{white-space:pre-wrap;background:#fafafa;padding:10px;border-radius:8px;font-size:12px;margin:8px 0 0}
.ops-row{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0 0 12px}
</style></head><body>
<div class="shell">
<h1>Every Fit 파일럿 관리자</h1>
<p class="sub">북마크 <code>/admin?token=...</code> · 수집 기간은 진단·퍼널 집계에 적용됩니다.</p>
<div id="admin-err"></div>
<div id="admin-loading" style="display:none">서버 응답 대기 중… (Render 슬립 시 30~60초)</div>
<div class="toolbar">
  <label>시작 <input type="date" id="dateFrom"/></label>
  <label>끝 <input type="date" id="dateTo"/></label>
  <button type="button" class="btn btn-ghost" data-preset="7">7일</button>
  <button type="button" class="btn btn-ghost" data-preset="30">30일</button>
  <button type="button" class="btn btn-ghost" data-preset="all">전체</button>
  <button type="button" class="btn btn-primary" id="applyRange">적용</button>
  <label style="flex:1;min-width:200px">진단번호
    <input type="text" id="dxLookup" placeholder="SF01-000001"/>
  </label>
  <button type="button" class="btn btn-primary" id="btnDxLookup">조회</button>
</div>
<div id="admin-meta" style="display:none"></div>
<div id="dx-detail"></div>
<nav class="tabs" aria-label="관리자 탭">
  <button type="button" class="on" data-tab="common">공통</button>
  <button type="button" data-tab="naver">네이버</button>
  <button type="button" data-tab="coupang">쿠팡</button>
  <button type="button" data-tab="workshop">발볼 작업실</button>
</nav>

<section id="panel-common" class="panel on">
  <h2>진단 추이 (일별)</h2>
  <div id="chart-daily" class="trend bar-chart"></div>
  <h2>SF 코드 분포</h2>
  <div id="chart-sf" class="bar-chart"></div>
  <h2>R 프로파일</h2>
  <div id="chart-r" class="bar-chart"></div>
  <h2>① 상세 → 간편 진단</h2>
  <div id="funnel-detail" class="cards"></div>
  <h2>② 정밀 진단</h2>
  <div id="funnel-precision" class="cards"></div>
  <h2>③ 사진 수신 (수기)</h2>
  <p class="sub" style="margin-top:0">앱 업로드 자동 · 010·카카오는 일별 수기</p>
  <div class="ops-row">
    <input type="date" id="photoDate"/>
    <input type="number" id="photoCount" min="0" placeholder="건수" style="width:80px"/>
    <input type="text" id="photoMemo" placeholder="메모" style="width:140px"/>
    <button type="button" class="btn btn-primary" id="savePhoto">일별 저장</button>
  </div>
  <div id="funnel-photo" class="cards"></div>
  <div class="table-wrap"><table><thead><tr><th>날짜</th><th>수신</th><th>메모</th><th>수정</th></tr></thead><tbody id="photoRows"></tbody></table></div>
  <h2>진단·코드 집계</h2>
  <div id="kpi" class="cards"></div>
  <h2>반품율 (3그룹)</h2>
  <div id="cohort" class="cards"></div>
  <h2>Foot profile (R/P/S)</h2>
  <p id="rps-prior-hint" class="sub"></p>
  <div id="rps-counts" class="cards"></div>
  <div class="table-wrap"><table><thead><tr><th>R</th><th>P</th><th>S</th><th>주문</th><th>반품</th><th>율</th><th>표본</th></tr></thead><tbody id="rpsPriorRows"></tbody></table></div>
  <h2>진단 목록</h2>
  <div class="ops-row">
    <input id="q" placeholder="진단번호·주문 검색" style="flex:1;min-width:160px;padding:8px;border-radius:8px;border:1px solid var(--border)"/>
    <select id="filterR"><option value="">R 전체</option><option>R1</option><option>R2</option><option>R3</option><option>R4</option><option>R5</option></select>
    <select id="filterP"><option value="">P 전체</option><option>P0</option><option>P1</option><option>P2</option><option>P3</option><option>P4</option><option>P5</option></select>
    <button type="button" class="btn btn-primary" id="search">검색</button>
  </div>
  <div class="table-wrap"><table><thead><tr>
    <th>진단번호</th><th>SF</th><th>R/P/S</th><th>mm</th><th>사진</th><th>주문</th><th>반품</th><th>사유</th><th>실작업</th><th>메모</th><th></th>
  </tr></thead><tbody id="rows"></tbody></table></div>
  <h2>진단 없음 주문</h2>
  <div class="ops-row">
    <input id="ono" placeholder="주문번호" style="flex:1;padding:8px;border-radius:8px;border:1px solid var(--border)"/>
    <select id="ret"><option value="0">반품 없음</option><option value="1">반품</option></select>
    <button type="button" class="btn btn-primary" id="addOrder">등록</button>
  </div>
</section>

<section id="panel-naver" class="panel">
  <h2>네이버 · 수기 카운터</h2>
  <div class="ops-row">
    <label>스토어 주문 <input type="number" id="opsNaverStore" min="0" style="width:72px"/></label>
    <label>SMS 발송 <input type="number" id="opsNaverSms" min="0" style="width:72px"/></label>
    <label>톡톡 문의 <input type="number" id="opsNaverTalk" min="0" style="width:72px"/></label>
    <input type="text" id="opsNaverMemo" placeholder="메모" style="width:120px"/>
    <button type="button" class="btn btn-primary" id="saveNaverOps">저장</button>
  </div>
  <h2>네이버 퍼널</h2>
  <div id="naver-funnel" class="cards"></div>
  <p id="naver-note" class="sub"></p>
  <h2>네이버 진단 추이</h2>
  <div id="chart-daily-naver" class="trend bar-chart"></div>
</section>

<section id="panel-coupang" class="panel">
  <h2>쿠팡 · 수기 카운터</h2>
  <div class="ops-row">
    <label>Wing 주문 <input type="number" id="opsWing" min="0" style="width:72px"/></label>
    <label>SMS <input type="number" id="opsSms" min="0" style="width:72px"/></label>
    <label>발볼 문의 <input type="number" id="opsInq" min="0" style="width:72px"/></label>
    <input type="text" id="opsMemo" placeholder="메모" style="width:120px"/>
    <button type="button" class="btn btn-primary" id="saveCoupangOps">저장</button>
  </div>
  <h2>쿠팡 퍼널</h2>
  <div id="coupang-funnel" class="cards"></div>
  <p id="coupang-note" class="sub"></p>
  <h2>쿠팡 진단 추이</h2>
  <div id="chart-daily-coupang" class="trend bar-chart"></div>
</section>

<section id="panel-workshop" class="panel">
  <h2>발볼 늘림 작업실</h2>
  <p class="sub">SF01~03 · SF05 · 정밀 완료 건. 미처리(실작업 비움) 우선 표시.</p>
  <div class="ops-row">
    <label><input type="checkbox" id="wsPending" checked/> 미처리만</label>
    <button type="button" class="btn btn-primary" id="wsReload">목록 새로고침</button>
    <a class="btn btn-ghost" id="wsSellerLink" href="#" target="_blank" rel="noopener">판매자 빠른답변</a>
  </div>
  <div class="table-wrap"><table><thead><tr>
    <th>진단번호</th><th>SF</th><th>정밀</th><th>R/P/S</th><th>주문</th><th>실작업</th><th>메모</th><th></th>
  </tr></thead><tbody id="wsRows"></tbody></table></div>
</section>
</div>
<script>
const token = (new URLSearchParams(location.search).get("token") || "").trim();
const h = { "X-Admin-Token": token };
const pct = (x)=> x!=null ? x+"%" : "-";
let kpiCache = null;

function qsRange(){
  const f=document.getElementById("dateFrom").value;
  const t=document.getElementById("dateTo").value;
  let q="";
  if(f) q+="&from_date="+encodeURIComponent(f);
  if(t) q+="&to_date="+encodeURIComponent(t);
  return q;
}
function card(label,val,hint){
  const v=val!=null?val:0;
  return '<div class="card">'+label+'<b>'+v+'</b>'+(hint?'<small>'+hint+'</small>':'')+'</div>';
}
function cardPct(label,val,hint){
  return '<div class="card">'+label+'<b class="pct">'+pct(val)+'</b><small>'+hint+'</small></div>';
}
function showErr(msg){
  const el=document.getElementById("admin-err");
  el.style.display=msg?"block":"none";
  el.textContent=msg||"";
}
function setLoading(on){
  document.getElementById("admin-loading").style.display=on?"block":"none";
  document.querySelectorAll(".cards").forEach(c=>c.classList.toggle("loading",!!on));
}
function barChart(elId, obj, order){
  const el=document.getElementById(elId);
  if(!el) return;
  const entries=order?order.map(k=>[k,obj[k]||0]):Object.entries(obj||{});
  const max=Math.max(1,...entries.map(e=>e[1]));
  el.innerHTML=entries.map(([k,v])=>'<div class="bar-row"><span class="lbl">'+k+'</span><span class="track"><span class="fill" style="width:'+Math.round(100*v/max)+'%"></span></span><span class="val">'+v+'</span></div>').join("")||'<p class="sub">데이터 없음</p>';
}
function trendChart(elId, days){
  const el=document.getElementById(elId);
  if(!el) return;
  const list=days||[];
  const max=Math.max(1,...list.map(d=>d.count));
  el.innerHTML=list.map(d=>'<div class="bar-row"><span class="lbl">'+d.day+'</span><span class="track"><span class="fill" style="width:'+Math.round(100*d.count/max)+'%"></span></span><span class="val">'+d.count+'</span></div>').join("")||'<p class="sub">기간 내 진단 없음</p>';
}
function showStorageMeta(storage, build, rule){
  const el=document.getElementById("admin-meta");
  if(!storage) return;
  const n=storage.diagnosis_count!=null?storage.diagnosis_count:"?";
  el.style.display="block";
  el.className=n===0?"warn":"";
  el.innerHTML="<b>저장</b> 진단 "+n+"건 · DB ~"+Math.round((storage.db_file_bytes||0)/1024)+"KB · 빌드 "+(build||"—")+" · 룰 "+(rule||"—")
    +(n===0&&storage.ephemeral_warning?"<br><br>"+storage.ephemeral_warning:"");
}
async function fetchRetry(url, opts, tries){
  tries=tries||4;
  for(let i=0;i<tries;i++){
    try{
      const r=await fetch(url,opts);
      if([502,503,504].includes(r.status)){ await new Promise(res=>setTimeout(res,1500*(i+1))); continue; }
      return r;
    }catch(e){ await new Promise(res=>setTimeout(res,1500*(i+1))); }
  }
  throw new Error("fetch failed");
}
function bindTabs(){
  document.querySelectorAll(".tabs button").forEach(btn=>{
    btn.onclick=()=>{
      document.querySelectorAll(".tabs button").forEach(b=>b.classList.remove("on"));
      document.querySelectorAll(".panel").forEach(p=>p.classList.remove("on"));
      btn.classList.add("on");
      const id="panel-"+btn.dataset.tab;
      const p=document.getElementById(id);
      if(p) p.classList.add("on");
      if(btn.dataset.tab==="workshop") loadWorkshop();
    };
  });
}
function setDefaultRange(days){
  const to=new Date();
  const from=new Date();
  if(days==="all"){
    document.getElementById("dateFrom").value="";
    document.getElementById("dateTo").value="";
    return;
  }
  const n=parseInt(days,10)||30;
  from.setDate(from.getDate()-(n-1));
  document.getElementById("dateFrom").value=from.toISOString().slice(0,10);
  document.getElementById("dateTo").value=to.toISOString().slice(0,10);
}
async function loadDxDetail(code){
  const box=document.getElementById("dx-detail");
  const c=(code||"").trim();
  if(!c){ box.style.display="none"; return; }
  const url="/api/admin/diagnoses/by-code/"+encodeURIComponent(c)+"?token="+encodeURIComponent(token);
  const r=await fetchRetry(url,{headers:h});
  if(!r.ok){ const e=await r.json().catch(()=>({})); showErr(e.detail||"진단 조회 실패"); return; }
  const j=await r.json();
  const d=j.diagnosis||{};
  const specs=(j.foot_compare&&j.foot_compare.customer&&j.foot_compare.customer.spec_lines)||[];
  const tl=(j.funnel_timeline||[]).map(e=>e.created_at+" · "+e.event+" ("+(e.channel||"")+")").join("\n");
  const sp=j.seller_preview||{};
  box.style.display="block";
  box.innerHTML='<h3>진단 상세 · '+d.diagnosis_code+'</h3><div class="dx-grid">'
    +'<div class="dx-block"><b>기본</b><br/>SF '+d.recommendation_code+' · '+d.channel+' · '+d.created_at
    +'<br/>Q1 '+esc(d.q1)+'<br/>Q2 '+esc(JSON.stringify(d.q2||[]))+'<br/>Q3 '+esc(d.q3)+' · Q4 '+d.q4+'mm'
    +'<br/>R/P/S '+(d.r_code||"-")+"/"+(d.p_code||"-")+"/"+(d.s_code||"-")
    +'</div><div class="dx-block"><b>발형 스펙</b><br/>'+specs.map(esc).join("<br/>")
    +'<br/><b>늘림 힌트</b> '+esc(JSON.stringify(j.stretch_hint||{}))
    +'</div><div class="dx-block"><b>판매자 문구(기본핏)</b><pre>'+esc(sp.reply_short||"")+'</pre></div>'
    +'<div class="dx-block"><b>퍼널</b><pre>'+esc(tl||"—")+'</pre></div></div>';
}
function esc(s){ return String(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
function rowHtml(r){
  const photo=r.photo_storage_key?'<a href="/api/admin/diagnoses/'+r.id+'/photo?token='+encodeURIComponent(token)+'" target="_blank" rel="noopener">보기</a>':"-";
  const rps=[r.r_code,r.p_code,r.s_code].filter(Boolean).join("/")||"-";
  return '<tr data-id="'+r.id+'">'
    +'<td><button type="button" class="btn btn-ghost btn-dx-open" data-code="'+esc(r.diagnosis_code)+'">'+esc(r.diagnosis_code)+'</button></td>'
    +'<td>'+esc(r.recommendation_code)+'</td><td>'+rps+'</td><td>'+(r.q4||"")+'</td><td>'+photo+'</td>'
    +'<td><input class="inp order" data-id="'+r.id+'" value="'+esc(r.order_no||"")+'"/></td>'
    +'<td><select class="inp ret" data-id="'+r.id+'"><option value="0" '+(r.return_status==0?"selected":"")+'>N</option><option value="1" '+(r.return_status==1?"selected":"")+'>Y</option></select></td>'
    +'<td><input class="inp reason" data-id="'+r.id+'" value="'+esc(r.return_reason||"")+'"/></td>'
    +'<td><select class="inp work" data-id="'+r.id+'"><option value="">-</option><option value="1" '+(r.actual_work_step==1?"selected":"")+'>1</option><option value="2" '+(r.actual_work_step==2?"selected":"")+'>2</option></select></td>'
    +'<td><textarea class="inp memo" data-id="'+r.id+'">'+esc(r.memo||"")+'</textarea></td>'
    +'<td><button type="button" class="btn btn-primary btn-save" data-id="'+r.id+'">저장</button></td></tr>';
}
function bindRowActions(){
  document.querySelectorAll(".btn-save").forEach(b=>b.onclick=()=>saveRow(b.dataset.id));
  document.querySelectorAll(".btn-dx-open").forEach(b=>b.onclick=()=>{
    document.getElementById("dxLookup").value=b.dataset.code;
    loadDxDetail(b.dataset.code);
  });
}
async function saveRow(id){
  const wsVal=document.querySelector('.work[data-id="'+id+'"]').value;
  const body={
    order_no:document.querySelector('.order[data-id="'+id+'"]').value,
    return_status:+document.querySelector('.ret[data-id="'+id+'"]').value,
    return_reason:document.querySelector('.reason[data-id="'+id+'"]').value,
    memo:document.querySelector('.memo[data-id="'+id+'"]').value
  };
  if(wsVal==="") body.actual_work_step=null;
  else body.actual_work_step=+wsVal;
  await fetch("/api/admin/diagnoses/"+id,{method:"PATCH",headers:{...h,"Content-Type":"application/json"},body:JSON.stringify(body)});
  load();
}
async function loadWorkshop(){
  const pending=document.getElementById("wsPending").checked;
  const url="/api/admin/diagnoses?token="+encodeURIComponent(token)+"&workshop=1"+(pending?"&pending_work=1":"")+qsRange();
  const r=await fetchRetry(url,{headers:h});
  const list=await r.json();
  document.getElementById("wsRows").innerHTML=(list.items||[]).map(r=>{
    const rps=[r.r_code,r.p_code,r.s_code].filter(Boolean).join("/")||"-";
    const prec=r.precision_completed?"완료":"-";
    return '<tr><td><button type="button" class="btn btn-ghost btn-dx-open" data-code="'+esc(r.diagnosis_code)+'">'+esc(r.diagnosis_code)+'</button></td>'
      +'<td>'+esc(r.recommendation_code)+'</td><td>'+prec+'</td><td>'+rps+'</td>'
      +'<td>'+esc(r.order_no||"-")+'</td>'
      +'<td><select class="inp ws-work" data-id="'+r.id+'"><option value="">-</option><option value="1" '+(r.actual_work_step==1?"selected":"")+'>1</option><option value="2" '+(r.actual_work_step==2?"selected":"")+'>2</option></select></td>'
      +'<td><textarea class="inp ws-memo" data-id="'+r.id+'">'+esc(r.memo||"")+'</textarea></td>'
      +'<td><button type="button" class="btn btn-primary ws-save" data-id="'+r.id+'">저장</button></td></tr>';
  }).join("")||'<tr><td colspan="8">해당 건 없음</td></tr>';
  document.querySelectorAll(".ws-save").forEach(b=>b.onclick=async()=>{
    const id=b.dataset.id;
    await fetch("/api/admin/diagnoses/"+id,{method:"PATCH",headers:{...h,"Content-Type":"application/json"},
      body:JSON.stringify({
        actual_work_step:document.querySelector('.ws-work[data-id="'+id+'"]').value||null,
        memo:document.querySelector('.ws-memo[data-id="'+id+'"]').value
      })});
    loadWorkshop();
  });
  document.querySelectorAll("#wsRows .btn-dx-open").forEach(b=>b.onclick=()=>loadDxDetail(b.dataset.code));
}
async function load(){
  if(!token){ showErr("URL에 ?token= 필요합니다."); return; }
  setLoading(true); showErr("");
  const kpiUrl="/api/admin/kpi?token="+encodeURIComponent(token)+qsRange();
  let kr;
  try{ kr=await fetchRetry(kpiUrl,{headers:h}); }catch(e){
    setLoading(false); showErr("서버 연결 실패. 슬립 중이면 잠시 후 새로고침."); return;
  }
  setLoading(false);
  if(!kr.ok){ showErr("KPI 실패 HTTP "+kr.status); return; }
  const k=await kr.json();
  kpiCache=k;
  showStorageMeta(k.storage,k.pilot_build,k.pilot_rule_version);
  const f=k.funnel||{};
  document.getElementById("funnel-detail").innerHTML=
    card("상세 노출",f.detail_views)+card("CTA",f.detail_cta_clicks)+card("진단(html)",f.diagnoses_html_detail)
    +cardPct("클릭율",f.click_rate_pct,"÷노출")+cardPct("전환",f.wide_conversion_pct,"÷노출");
  document.getElementById("funnel-precision").innerHTML=
    card("정밀 폼",f.precision_form_views)+card("입력 시작",f.precision_input_started)+card("접수",f.precision_completed)
    +cardPct("제출율",f.precision_submit_rate_pct,"÷폼")+card("앱 사진",f.precision_photo_app_uploads);
  document.getElementById("funnel-photo").innerHTML=
    card("문자 수신",f.photo_received_total)+cardPct("커버리지",f.photo_combined_after_precision_pct,"참고");
  document.getElementById("photoRows").innerHTML=(f.photo_daily||[]).map(r=>'<tr><td>'+r.log_date+'</td><td>'+r.photo_count+'</td><td>'+(r.memo||"")+'</td><td>'+(r.updated_at||"")+'</td></tr>').join("")||'<tr><td colspan="4">없음</td></tr>';
  const labels={total_diagnoses:"전체",sf01:"SF01",sf02:"SF02",sf03:"SF03",sf04:"SF04",sf05:"SF05",sf00:"SF00",complex_case:"복합",precision_completed:"정밀",orders_registered:"주문",returns_registered:"반품"};
  document.getElementById("kpi").innerHTML=Object.entries(k.counts||{}).map(([key,v])=>card(labels[key]||key,v)).join("");
  const cohortLabels={none:"진단없음",diagnosis_only:"진단만",diagnosis_stretch:"진단+늘림"};
  document.getElementById("cohort").innerHTML=Object.entries(cohortLabels).map(([key,label])=>{
    const x=(k.cohort||{})[key]||{};
    return card(label,(x.return_rate_pct!=null?x.return_rate_pct+"%":"-"),"주문 "+(x.orders||0));
  }).join("");
  const fp=k.foot_profile||{};
  document.getElementById("rps-prior-hint").textContent="반품 prior · 표본 "+(fp.prior_min_orders||3)+"건 미만 부족";
  document.getElementById("rps-counts").innerHTML=card("R 종류",Object.keys(fp.by_r||{}).length)+card("P 종류",Object.keys(fp.by_p||{}).length)+card("미백필",fp.missing_profile_count||0);
  document.getElementById("rpsPriorRows").innerHTML=(fp.return_priors||[]).map(row=>'<tr><td>'+row.r_code+'</td><td>'+row.p_code+'</td><td>'+row.s_code+'</td><td>'+row.orders+'</td><td>'+row.returns+'</td><td>'+(row.return_rate_pct!=null?row.return_rate_pct+"%":"-")+'</td><td>'+(row.sufficient?"충분":"부족")+'</td></tr>').join("")||'<tr><td colspan="7">없음</td></tr>';
  barChart("chart-sf",{SF01:k.counts.sf01,SF02:k.counts.sf02,SF03:k.counts.sf03,SF04:k.counts.sf04,SF05:k.counts.sf05,SF00:k.counts.sf00},["SF01","SF02","SF03","SF04","SF05","SF00"]);
  barChart("chart-r",fp.by_r||{});
  trendChart("chart-daily",k.daily_diagnoses||[]);
  trendChart("chart-daily-naver",k.daily_naver||[]);
  trendChart("chart-daily-coupang",k.daily_coupang||[]);
  const cg=k.coupang||{};
  const ops=cg.ops||{};
  if(ops.coupang_wing_orders) document.getElementById("opsWing").value=ops.coupang_wing_orders.value||0;
  if(ops.coupang_sms_sent) document.getElementById("opsSms").value=ops.coupang_sms_sent.value||0;
  if(ops.coupang_inquiry_inbound) document.getElementById("opsInq").value=ops.coupang_inquiry_inbound.value||0;
  document.getElementById("coupang-funnel").innerHTML=
    card("coupang 진단",cg.coupang_sms_diagnoses)+card("랜딩",cg.coupang_sms_landings)
    +cardPct("SMS→랜딩",cg.rate_sms_to_landing_pct,"")+cardPct("랜딩→진단",cg.rate_landing_to_diagnosis_pct,"");
  document.getElementById("coupang-note").textContent=cg.note||"";
  const nv=k.naver||{};
  const nops=nv.ops||{};
  if(nops.naver_store_orders) document.getElementById("opsNaverStore").value=nops.naver_store_orders.value||0;
  if(nops.naver_sms_sent) document.getElementById("opsNaverSms").value=nops.naver_sms_sent.value||0;
  if(nops.naver_talktalk_inbound) document.getElementById("opsNaverTalk").value=nops.naver_talktalk_inbound.value||0;
  document.getElementById("naver-funnel").innerHTML=
    card("naver 진단",nv.naver_diagnoses)+card("랜딩",nv.naver_landings)+card("결과뷰",nv.naver_result_views)
    +card("교환복사",nv.naver_exchange_copies)+card("톡톡열기",nv.talktalk_open)
    +cardPct("결과→복사",nv.rate_result_to_copy_pct,"")+card("정밀폼",nv.precision_form_views);
  document.getElementById("naver-note").textContent=nv.note||"";
  const listUrl="/api/admin/diagnoses?token="+encodeURIComponent(token)+"&q="+encodeURIComponent(document.getElementById("q").value||"")+"&r_code="+encodeURIComponent(document.getElementById("filterR").value||"")+"&p_code="+encodeURIComponent(document.getElementById("filterP").value||"")+qsRange();
  const lr=await fetchRetry(listUrl,{headers:h},3);
  const list=await lr.json();
  document.getElementById("rows").innerHTML=(list.items||[]).map(rowHtml).join("");
  bindRowActions();
}
document.getElementById("applyRange").onclick=load;
document.getElementById("search").onclick=load;
document.querySelectorAll("[data-preset]").forEach(b=>b.onclick=()=>{ setDefaultRange(b.dataset.preset); load(); });
document.getElementById("btnDxLookup").onclick=()=>loadDxDetail(document.getElementById("dxLookup").value);
document.getElementById("savePhoto").onclick=async()=>{
  const d=document.getElementById("photoDate").value;
  const res=await fetch("/api/admin/photo-daily",{method:"PUT",headers:{...h,"Content-Type":"application/json"},
    body:JSON.stringify({log_date:d,photo_count:+(document.getElementById("photoCount").value||0),memo:document.getElementById("photoMemo").value||""})});
  if(!res.ok){ alert("저장 실패"); return; }
  load();
};
document.getElementById("saveCoupangOps").onclick=async()=>{
  const body={wing_orders:+(document.getElementById("opsWing").value||0),sms_sent:+(document.getElementById("opsSms").value||0),inquiry_inbound:+(document.getElementById("opsInq").value||0),memo:document.getElementById("opsMemo").value||""};
  await fetch("/api/admin/coupang-ops",{method:"PUT",headers:{...h,"Content-Type":"application/json"},body:JSON.stringify(body)});
  load();
};
document.getElementById("saveNaverOps").onclick=async()=>{
  const body={store_orders:+(document.getElementById("opsNaverStore").value||0),sms_sent:+(document.getElementById("opsNaverSms").value||0),talktalk_inbound:+(document.getElementById("opsNaverTalk").value||0),memo:document.getElementById("opsNaverMemo").value||""};
  await fetch("/api/admin/naver-ops",{method:"PUT",headers:{...h,"Content-Type":"application/json"},body:JSON.stringify(body)});
  load();
};
document.getElementById("addOrder").onclick=async()=>{
  await fetch("/api/admin/orders/no-diagnosis",{method:"POST",headers:{...h,"Content-Type":"application/json"},
    body:JSON.stringify({order_no:document.getElementById("ono").value,return_status:+document.getElementById("ret").value})});
  load();
};
document.getElementById("wsReload").onclick=loadWorkshop;
document.getElementById("wsSellerLink").href="/seller/quick?token="+encodeURIComponent(token);
bindTabs();
setDefaultRange(30);
document.getElementById("photoDate").value=new Date().toISOString().slice(0,10);
load();
</script></body></html>"""
