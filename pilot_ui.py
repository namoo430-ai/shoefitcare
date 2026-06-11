"""파일럿 / 관리자 HTML (FastAPI에서 로드)."""

PILOT_HTML = """<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>슈핏케어 · 내 발에 맞는 핏 찾기</title>
<style>
:root{--pink:#c97b84;--bg:#f2f2f7;--card:#fff;--muted:#6b7280;--border:#e5e5ea;--text:#1c1c1e}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased}
.wrap{max-width:430px;margin:0 auto;padding:12px 14px 80px}
.card{background:var(--card);border-radius:16px;padding:16px;margin:10px 0;border:1px solid var(--border)}
h1{font-size:17px;margin:0 0 6px;font-weight:700;line-height:1.4}
h2.prec-h2{font-size:16px;margin:0 0 8px;font-weight:700;line-height:1.4}
p.sub{color:var(--muted);font-size:14px;line-height:1.55;margin:0}
.step-progress{font-size:13px;color:var(--pink);margin:0 0 10px;font-weight:600}
#step h1{line-height:1.45;margin:0 0 12px}
#step .sub{margin:0 0 16px}
.step-choices{display:flex;flex-direction:column;gap:10px}
.step-choices .btn{margin:0;line-height:1.5;padding:14px 12px}
.chips-row{display:flex;flex-wrap:wrap;gap:10px}
.chips-col{display:flex;flex-direction:column;gap:10px}
.chips-col .chip{display:block;width:100%;text-align:left;padding:12px 14px;line-height:1.5;box-sizing:border-box;border-radius:12px}
.cta-wrap{margin-top:24px;padding-top:20px;border-top:1px solid #e8e8ed}
.cta-wrap .btn.primary{margin:0}
.btn-step-back{display:block;width:100%;margin:12px 0 0;padding:12px;border-radius:12px;border:1px solid var(--border);background:#fff;color:var(--muted);font-size:15px;font-weight:500;cursor:pointer;text-align:center;font-family:inherit}
.btn-step-back:active{background:#f9f9fb}
.btn{display:block;width:100%;margin:6px 0;padding:12px 12px 12px 14px;border-radius:12px;border:2px solid #e0e0e5;background:#fff;font-size:15px;cursor:pointer;text-align:left;line-height:1.5;transition:border-color .15s,background .15s,box-shadow .15s}
.step-choices .btn.on{position:relative;border-color:var(--pink);background:#fdf5f6;color:#c25d68;font-weight:700;box-shadow:0 0 0 3px rgba(201,123,132,.28)}
.step-choices .btn.on::before{content:"✓";position:absolute;left:12px;top:50%;transform:translateY(-50%);font-size:16px;font-weight:700;color:var(--pink)}
.step-choices .btn.on{padding-left:38px}
.btn.primary{background:var(--pink);color:#fff;border:0;text-align:center;font-weight:600}
.chip{padding:10px 14px;border-radius:12px;border:2px solid #e0e0e5;background:#fff;font-size:15px;cursor:pointer;line-height:1.45;transition:border-color .15s,background .15s,box-shadow .15s}
.chips-row .chip.on,.chips-col .chip.on{background:var(--pink);color:#fff;border-color:var(--pink);font-weight:700;box-shadow:0 0 0 3px rgba(201,123,132,.28)}
.hidden{display:none}
.result-msg{white-space:pre-wrap;font-size:15px;line-height:1.55;margin:0 0 10px;font-family:inherit;color:inherit}
.result-dx{margin:12px 0 8px;font-size:15px}
.result-hint{margin:6px 0;line-height:1.55;font-size:14px}
.result-footnote{margin:14px 0 0;font-size:13px;color:var(--muted);line-height:1.5;text-align:center}
.result-cta{margin-top:12px;padding-top:0;border-top:0}
.result-next-wrap{margin-top:20px;padding-top:18px;border-top:1px solid #e8e8ed}
.result-next-hint{font-size:13px;color:var(--muted);line-height:1.5;margin:0 0 12px;text-align:center}
.btn-result-next{display:block;width:100%;padding:14px 12px;border-radius:12px;border:1px solid var(--pink);background:#fff;color:var(--pink);font-size:15px;font-weight:600;cursor:pointer;text-align:center;font-family:inherit;line-height:1.45}
.btn-result-next:active{background:#fdf5f6}
.result-detail-back-wrap{margin-top:20px;padding-top:4px}
.result-detail-back-wrap .result-back-hint{font-size:13px;color:var(--muted);line-height:1.5;margin:0 0 12px;text-align:center}
.prec-step-head{margin:0 0 16px}
.prec-step-head h2{font-size:16px;margin:0 0 8px;line-height:1.45;font-weight:700}
.prec-step-head p{font-size:14px;line-height:1.55;color:var(--muted);margin:0}
input{width:100%;padding:11px 12px;border-radius:10px;border:1px solid var(--border);margin:0;font-size:15px;box-sizing:border-box;background:#fff;color:var(--text)}
label.field-label{display:block;font-size:13px;color:var(--muted);margin:0 0 6px;font-weight:500}
.prec-block{border:1px solid var(--border);border-radius:12px;padding:14px;margin:0 0 12px;background:#fafafa}
.prec-block-title{font-size:15px;font-weight:700;margin:0 0 12px;display:flex;align-items:center;gap:6px}
.prec-field{margin:0 0 12px}
.prec-field:last-child{margin-bottom:0}
.prec-section{margin:0 0 12px}
.prec-section-title{font-size:15px;font-weight:700;margin:0 0 4px;display:flex;align-items:center;gap:6px}
.prec-section-note{font-size:13px;color:var(--muted);margin:0 0 10px;line-height:1.45}
.prec-photo{border:1px solid var(--border);border-radius:12px;padding:14px;margin:16px 0;background:#fff}
.prec-photo p{font-size:14px;line-height:1.55;margin:0 0 8px;color:var(--text)}
.prec-photo-alt{font-size:13px;color:var(--muted);line-height:1.5;margin:10px 0 0}
.prec-photo-preview{display:block;max-width:100%;max-height:160px;margin:10px auto 0;border-radius:8px}
.prec-photo-file{width:100%;font-size:14px;margin-top:8px}
.prec-phone{font-size:15px;font-weight:700;letter-spacing:0.02em;margin:0}
.prec-consent{display:flex;align-items:flex-start;gap:8px;margin:12px 0 0;font-size:13px;line-height:1.45;color:var(--text)}
.prec-consent input[type=checkbox]{width:18px;height:18px;margin:2px 0 0;flex-shrink:0}
.btn-prec-submit{display:flex;align-items:center;justify-content:center;box-sizing:border-box;margin-top:8px;border-radius:12px;padding:14px;font-size:16px;font-weight:600;background:var(--pink);color:#fff;border:0;width:100%;cursor:pointer;text-align:center;font-family:inherit}
.prec-done-title{font-size:17px;font-weight:700;margin:0 0 14px;line-height:1.45}
.prec-done p{font-size:15px;line-height:1.6;margin:0 0 12px;color:var(--text)}
.prec-done p:last-of-type{margin-bottom:20px}
.btn-detail-back{display:block;width:100%;text-align:center;text-decoration:none;border-radius:12px;padding:14px;font-size:15px;font-weight:600;background:#fff;color:var(--pink);border:1px solid var(--pink);cursor:pointer;box-sizing:border-box}
</style></head><body>
<div class="wrap">
  <div class="card"><h1>내 발에 맞는 핏 찾기</h1>
  <p class="sub">4개의 간단한 질문으로 편안한 핏을 추천해 드려요.<br><span style="font-size:13px">약 30초 소요</span></p>
  <p style="font-size:11px;color:#c97b84">빌드 __PILOT_BUILD__</p></div>
  <div id="step" class="card"></div>
  <div id="result" class="card hidden"></div>
  <div id="prec-teaser" class="card hidden prec-teaser"></div>
  <div id="precision" class="card hidden"></div>
</div>
<script>
const sizes = [225,230,235,240,245,250,255];
const params = new URLSearchParams(location.search);
const productId = params.get("product_id") || "";
const src = params.get("src") || "web";
const returnUrl = (params.get("return_url") || params.get("order_url") || "").trim();
const coupangChannel = /^coupang/i.test(src);
function productDetailHref(){
  const q = productId ? "?product_id="+encodeURIComponent(productId) : "";
  return location.origin+"/product-detail"+q;
}
function orderPageHref(){
  if(returnUrl) return returnUrl;
  if(coupangChannel) return "";
  return productDetailHref();
}
function orderBackLabel(){
  if(returnUrl || coupangChannel) return "쿠팡에서 주문하기";
  return "주문 페이지로 돌아가기";
}
function orderBackHint(recommendationCode){
  if(returnUrl || coupangChannel){
    return recommendationCode==="SF00"
      ? '<p class="result-back-hint">안내 확인 후 아래 버튼으로 <b>쿠팡 상품 페이지</b>에서 사이즈를 선택해 주문해 주세요.</p>'
      : '<p class="result-back-hint">발볼 안내·문의 후 주문하시려면 <b>쿠팡 상품 페이지</b>로 돌아가 주세요.</p>';
  }
  return recommendationCode==="SF00"
    ? '<p class="result-back-hint">안내를 확인하신 뒤, 아래 버튼으로 주문 페이지에서 사이즈를 선택해 주세요.</p>'
    : "";
}
function resultDetailBackHtml(recommendationCode){
  const href = orderPageHref();
  const hint = orderBackHint(recommendationCode);
  if(!href){
    return '<div class="result-detail-back-wrap">'+hint
      +'<p class="result-back-hint">쿠팡 앱으로 돌아가 상품 페이지에서 주문해 주세요.</p></div>';
  }
  return '<div class="result-detail-back-wrap">'+hint
    +'<a class="btn-detail-back" href="'+href+'" rel="noopener">'+orderBackLabel()+'</a></div>';
}
function postPilotFunnelEvent(eventName, dxId){
  const body = {event:eventName, product_id:productId||null, channel:src};
  const id = dxId || diagnosisId;
  if(id) body.diagnosis_id = id;
  fetch("/pilot/event",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify(body), keepalive:true}).catch(()=>{});
}
let answers = { q1:"", q2:[], q3:"", q4:235 };
let diagnosisId = "";
let step = 0;
const Q1_NONE = "특별히 불편함이 없어요";
const Q2_NONE = "불편 사항 없음";
const Q3_NONE = "불편은 거의 없어요";
function finishQ1NoDiscomfort(){
  answers.q1 = Q1_NONE;
  answers.q2 = [Q2_NONE];
  answers.q3 = Q3_NONE;
  submit();
}
const steps = [
  { key:"q1", title:"평소 어떤 불편함이 있으셨나요?", single:true, nextBtn:"내 발 상태 확인하기 →", opts:[
    "길이는 맞는데 발볼이 조이는 편이에요","발볼 때문에 큰 사이즈를 신으면 헐거워져요",
    "발등이 눌리는 편이에요","대부분 신발이 여유 있는 편이에요", Q1_NONE]},
  { key:"q2", title:"어디가 가장 불편하셨나요?", hint:"해당되는 부위를 모두 선택해 주세요.", multi:true, nextBtn:"추천 계속 받기 →", opts:[
    "엄지발가락 옆(무지외반)","발볼 부분","발등 부분","새끼 발가락쪽",Q2_NONE]},
  { key:"q3", title:"불편한 정도는 어느 쯤인가요?", single:true, nextBtn:"거의 다 됐어요 →", opts:[
    "가끔 신경 쓰여요","자주 불편해요","매우 불편해요",Q3_NONE]},
  { key:"q4", title:"보통 어떤 사이즈를 주문하시나요?", size:true, nextBtn:"추천 결과 보기 →" },
];
function precisionStepHtml(){
  return '<div class="prec-step-head">'
    +'<h2>🔍 더 정확한 발볼 조절을 원하시나요?</h2>'
    +'<p>아래에 발 치수를 입력하고, 가능하면 발 모양 사진도 올려 주세요.</p></div>'
    +'<div class="prec-block"><p class="prec-block-title">📏 왼발</p>'
    +'<div class="prec-field"><label class="field-label" for="l1">길이 (cm)</label><input id="l1" type="number" step="0.1" inputmode="decimal" placeholder="예: 25.3"></div>'
    +'<div class="prec-field"><label class="field-label" for="lw">너비 (cm)</label><input id="lw" type="number" step="0.1" inputmode="decimal" placeholder="예: 9.8"></div></div>'
    +'<div class="prec-block"><p class="prec-block-title">📏 오른발</p>'
    +'<div class="prec-field"><label class="field-label" for="r1">길이 (cm)</label><input id="r1" type="number" step="0.1" inputmode="decimal" placeholder="예: 25.0"></div>'
    +'<div class="prec-field"><label class="field-label" for="rw">너비 (cm)</label><input id="rw" type="number" step="0.1" inputmode="decimal" placeholder="예: 10.1"></div></div>'
    +'<div class="prec-section"><p class="prec-section-title">📞 연락처</p>'
    +'<p class="prec-section-note">진단 결과 안내용으로만 사용됩니다.</p>'
    +'<input id="ct" type="tel" inputmode="numeric" maxlength="11" placeholder="숫자만 입력 (예: 01012345678)"></div>'
    +'<label class="prec-consent"><input type="checkbox" id="consent"> 진단 결과 안내를 위한 연락처 수집에 동의합니다.</label>'
    +'<div class="prec-photo"><p class="prec-section-title" style="margin-bottom:8px">📷 발 모양 사진 올리기 (권장)</p>'
    +'<p>종이에 발 모양을 그리고, 주문자 이름이 보이게 촬영한 뒤 아래에서 선택해 주세요.</p>'
    +'<input class="prec-photo-file" type="file" id="footPhoto" accept="image/jpeg,image/png,image/webp" capture="environment">'
    +'<img class="prec-photo-preview hidden" id="footPhotoPreview" alt="">'
    +'<p class="prec-photo-alt">업로드가 어려우시면 같은 사진을 <b>010-8931-6325</b>로 보내주셔도 됩니다.</p></div>'
    +'<button type="button" class="btn-prec-submit" id="psave">정확하게 진단받기</button>';
}
function precisionCompleteHtml(opts){
  opts = opts || {};
  const href = orderPageHref();
  const photoNote = opts.photoUploaded
    ? '<p class="sub">발 모양 사진이 함께 접수되었습니다.</p>'
    : '<p class="sub">사진을 아직 올리지 않으셨다면, 종이에 그린 발 모양을 주문자 이름과 함께 <b>010-8931-6325</b>로 보내주셔도 됩니다.</p>';
  return '<div class="prec-done">'
    +'<p class="prec-done-title">정밀 진단 접수가 완료되었습니다. 👣</p>'
    +photoNote
    +'<p>보내주신 발 모양 사진과 입력해 주신 정밀 진단 정보를 함께 분석한 후, 간편 진단 결과를 반영하여 보다 정확한 발볼 늘림 안내 정보를 카카오톡으로 안내해 드립니다.</p>'
    +'<p>진단 결과는 보통 1~2시간 내 확인하실 수 있으며, 순차적으로 안내드리고 있습니다.</p>'
    +'<p>감사합니다. 😊</p>'
    +(href
      ? '<a class="btn-detail-back" href="'+href+'" rel="noopener">'+orderBackLabel()+'</a>'
      : '<p class="result-back-hint">쿠팡 앱으로 돌아가 주문해 주세요.</p>')
    +'</div>';
}
function showPrecisionComplete(opts){
  document.getElementById("prec-teaser").classList.add("hidden");
  const p = document.getElementById("precision");
  p.classList.remove("hidden");
  p.innerHTML = precisionCompleteHtml(opts);
  postPilotFunnelEvent("precision_complete_view", diagnosisId);
  p.scrollIntoView({behavior:"smooth", block:"start"});
}
function bindPhotoPreview(){
  const inp = document.getElementById("footPhoto");
  const prev = document.getElementById("footPhotoPreview");
  if(!inp || !prev) return;
  inp.onchange = ()=>{
    const f = inp.files && inp.files[0];
    if(!f){ prev.classList.add("hidden"); return; }
    prev.src = URL.createObjectURL(f);
    prev.classList.remove("hidden");
  };
}
function bindPrecisionInputTracking(){
  const key = "sf_prec_in:"+diagnosisId;
  const fire = ()=>{
    if(sessionStorage.getItem(key)==="1") return;
    sessionStorage.setItem(key,"1");
    postPilotFunnelEvent("precision_input_started", diagnosisId);
  };
  ["l1","lw","r1","rw"].forEach(id=>{
    const el = document.getElementById(id);
    if(el) el.addEventListener("input", fire, {once:true});
  });
}
function showPrecisionBlocks(hideResult){
  if(hideResult) document.getElementById("result").classList.add("hidden");
  document.getElementById("prec-teaser").classList.add("hidden");
  const p = document.getElementById("precision");
  p.classList.remove("hidden");
  p.innerHTML = precisionStepHtml();
  bindPrecisionSave();
  bindPrecisionInputTracking();
  bindPhotoPreview();
  postPilotFunnelEvent("precision_form_view", diagnosisId);
  p.scrollIntoView({behavior:"smooth", block:"start"});
}
function bindPrecisionSave(){
  document.getElementById("psave").onclick = async ()=>{
    if(!document.getElementById("consent").checked){ alert("동의가 필요합니다."); return; }
    const contact = document.getElementById("ct").value.replace(/\\D/g, "");
    if(!contact){ alert("연락처를 숫자만 입력해 주세요."); return; }
    const pr = await fetch("/pilot/precision",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({diagnosis_id:diagnosisId,
        left_length_cm:+document.getElementById("l1").value,
        right_length_cm:+document.getElementById("r1").value,
        left_width_cm:+document.getElementById("lw").value,
        right_width_cm:+document.getElementById("rw").value,
        contact:contact, consent:true})});
    const pd = await pr.json();
    if(pd.error){ alert(pd.error); return; }
    let photoUploaded = false;
    const fileInp = document.getElementById("footPhoto");
    const file = fileInp && fileInp.files && fileInp.files[0];
    if(file){
      const fd = new FormData();
      fd.append("diagnosis_id", diagnosisId);
      fd.append("photo", file);
      const up = await fetch("/pilot/precision-photo",{method:"POST", body:fd});
      const ud = await up.json();
      if(ud.error){
        alert("사진 업로드에 실패했습니다. 접수는 완료되었습니다.\\n"+ud.error+"\\n010-8931-6325로 보내주셔도 됩니다.");
      } else {
        photoUploaded = true;
      }
    }
    showPrecisionComplete({photoUploaded:photoUploaded});
  };
}
function render(){
  const el = document.getElementById("step");
  if(step >= steps.length){ submit(); return; }
  const s = steps[step];
  let html = '<p class="step-progress">'+(step+1)+' / 4</p><h1>'+s.title+"</h1>";
  if(s.hint){ html += '<p class="sub">'+s.hint+'</p>'; }
  if(s.size){
    html += '<div class="step-choices chips-row">'+sizes.map(v=>'<span class="chip'+(answers.q4===v?" on":"")+'" data-v="'+v+'">'+v+'</span>').join("")+'</div>';
  } else if(s.multi){
    html += '<div class="step-choices chips-col">'+s.opts.map(o=>'<span class="chip'+(answers.q2.includes(o)?" on":"")+'" data-o="'+o+'">'+o+'</span>').join("")+'</div>';
  } else {
    html += '<div class="step-choices">';
    s.opts.forEach(o=>{ html += '<button type="button" class="btn'+(answers[s.key]===o?" on":"")+'" data-o="'+o+'">'+o+'</button>'; });
    html += '</div>';
  }
  html += '<div class="cta-wrap"><button type="button" class="btn primary" id="next">'+(s.nextBtn||"다음")+'</button>';
  if(step > 0){
    html += '<button type="button" class="btn-step-back" id="step-back">이전 화면으로</button>';
  }
  html += '</div>';
  el.innerHTML = html;
  el.querySelectorAll(".btn[data-o], .chip").forEach(b=>{
    b.onclick = ()=>{
      const o = b.dataset.o || b.dataset.v;
      if(s.size){ answers.q4 = parseInt(o,10); render(); return; }
      if(s.multi){
        if(o===Q2_NONE){ answers.q2=[o]; }
        else {
          answers.q2 = answers.q2.filter(x=>x!==Q2_NONE);
          if(answers.q2.includes(o)) answers.q2 = answers.q2.filter(x=>x!==o);
          else answers.q2.push(o);
        }
        render(); return;
      }
      answers[s.key]=o;
      if(s.key==="q1" && o===Q1_NONE){ finishQ1NoDiscomfort(); return; }
      render();
    };
  });
  document.getElementById("next").onclick = ()=>{
    if(s.multi && !answers.q2.length){ alert("항목을 선택해 주세요."); return; }
    if(!s.multi && !s.size && !answers[s.key]){ alert("선택해 주세요."); return; }
    step++; render();
  };
  const backBtn = document.getElementById("step-back");
  if(backBtn){
    backBtn.onclick = ()=>{ if(step > 0){ step--; render(); } };
  }
}
async function submit(){
  document.getElementById("step").classList.add("hidden");
  const res = await fetch("/pilot/diagnose",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({...answers, product_id:productId, channel:src})});
  const data = await res.json();
  diagnosisId = data.id;
  postPilotFunnelEvent("pilot_result_view", diagnosisId);
  const r = document.getElementById("result");
  r.classList.remove("hidden");
  const code = data.recommendation_code;
  const stretch = code==="SF01" || code==="SF02";
  const sf00 = code==="SF00";
  const prec = !!data.precision_recommended;
  const copyLabel = stretch ? "발볼 늘림 안내문 복사하기" : "안내문 복사하기";
  const copyText = data.inquiry_copy_text || (data.message+"\\n\\n진단번호: "+data.diagnosis_code);
  const ctaLabel = (prec && !stretch) ? "정밀 진단 받아보기" : copyLabel;
  const ctaId = (prec && !stretch) ? "prec-cta" : "copy";
  const primaryCta = sf00 ? "" : '<div class="cta-wrap result-cta"><button class="btn primary" id="'+ctaId+'">'+ctaLabel+'</button></div>';
  const stretchHints = stretch
    ? '<p class="sub result-hint">📌 문의글 작성 시 진단번호를 꼭 남겨주세요.</p>'
      +'<p class="sub result-hint">👇 아래 버튼을 누르면 진단번호와 진단 결과가 함께 복사됩니다.</p>'
    : "";
  const stretchFoot = stretch
    ? '<p class="result-footnote">※ 진단번호 누락 시 접수가 지연될 수 있습니다.</p>'
    : "";
  const precNextBlock = (prec && stretch)
    ? '<div class="result-next-wrap hidden" id="prec-next-wrap">'
      +'<p class="result-next-hint">더 정확한 발볼 조절이 필요하시면 다음 단계를 진행해 주세요.</p>'
      +'<button type="button" class="btn-result-next" id="prec-next">🔍 더 정확한 발볼 조절 받기 (선택)</button></div>'
    : "";
  r.innerHTML = '<div class="result-msg">'+data.message+'</div>'
    +'<p class="result-dx"><b>진단번호: '+data.diagnosis_code+'</b></p>'
    +stretchHints
    +primaryCta
    +stretchFoot
    +precNextBlock
    +resultDetailBackHtml(data.recommendation_code);
  document.getElementById("prec-teaser").classList.add("hidden");
  document.getElementById("precision").classList.add("hidden");
  if(prec && !stretch){
    document.getElementById("prec-cta").onclick = ()=>{ showPrecisionBlocks(true); };
  }
  if(document.getElementById("copy")){
    document.getElementById("copy").onclick = async ()=>{
      await navigator.clipboard.writeText(copyText);
      postPilotFunnelEvent("pilot_copy_inquiry", diagnosisId);
      const b=document.getElementById("copy");
      const prev=b.textContent;
      b.textContent="복사했어요!";
      setTimeout(()=>{ b.textContent=prev; }, 1500);
      const wrap = document.getElementById("prec-next-wrap");
      if(wrap) wrap.classList.remove("hidden");
    };
  }
  const precNext = document.getElementById("prec-next");
  if(precNext){
    precNext.onclick = ()=>{ showPrecisionBlocks(true); };
  }
  r.scrollIntoView({behavior:"smooth", block:"start"});
}
render();
</script></body></html>"""

ADMIN_HTML = """<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>슈핏케어 관리자</title>
<style>
body{font-family:system-ui,sans-serif;margin:16px;background:#f8fafc}
.cards{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:16px}
.card{background:#fff;padding:12px 16px;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.08);min-width:120px}
.card b{display:block;font-size:22px}
table{border-collapse:collapse;width:100%;background:#fff;font-size:13px}
th,td{border:1px solid #e2e8f0;padding:8px;text-align:left}
input,select{padding:6px;font-size:13px}
h2{margin:20px 0 8px;font-size:16px}
.card small{display:block;font-size:11px;color:#64748b;margin-top:4px}
.card .pct{font-size:14px;font-weight:600;color:#c97b84}
</style></head><body>
<h1>슈핏케어 파일럿 관리자</h1>
<p class="sub">토큰: URL에 <code>?token=...</code> (환경변수 ADMIN_TOKEN)</p>
<div id="admin-err" style="display:none;margin:12px 0;padding:12px;border-radius:8px;background:#fef2f2;color:#991b1b;font-size:14px"></div>
<h2>① 상세 → 간편 진단</h2>
<div id="funnel-detail" class="cards"></div>
<h2>② 정밀 진단 (발치수 → 접수 완료)</h2>
<div id="funnel-precision" class="cards"></div>
<h2>③ 발 모양 사진 수신 (수기)</h2>
<p style="font-size:13px;color:#64748b;margin:0 0 8px">앱 업로드는 자동 집계됩니다. <b>010·카카오로만 받은 사진</b>은 일별 건수를 수기 입력하세요.</p>
<div style="margin-bottom:12px">
  <input type="date" id="photoDate"/>
  <input type="number" id="photoCount" min="0" placeholder="수신 건수" style="width:100px"/>
  <input type="text" id="photoMemo" placeholder="메모(선택)" style="width:160px"/>
  <button type="button" id="savePhoto">일별 저장</button>
</div>
<div id="funnel-photo" class="cards"></div>
<table><thead><tr><th>날짜</th><th>사진 수신</th><th>메모</th><th>수정 시각</th></tr></thead>
<tbody id="photoRows"></tbody></table>
<h2>진단·코드 집계</h2>
<div id="kpi" class="cards"></div>
<h2>반품율 (3그룹)</h2>
<div id="cohort" class="cards"></div>
<h2>진단 목록</h2>
<input id="q" placeholder="진단번호 검색"/> <button id="search">검색</button>
<table><thead><tr>
<th>진단번호</th><th>코드</th><th>사이즈</th><th>사진</th><th>주문</th><th>반품</th><th>실작업</th><th>저장</th>
</tr></thead><tbody id="rows"></tbody></table>
<h2>진단 없음 주문 등록</h2>
<input id="ono" placeholder="주문번호"/>
<select id="ret"><option value="0">반품 없음</option><option value="1">반품</option></select>
<button id="addOrder">등록</button>
<script>
const token = (new URLSearchParams(location.search).get("token") || "").trim();
const h = { "X-Admin-Token": token };
const pct = (x)=> x!=null ? x+"%" : "-";
function card(label, val, hint){
  const v = val!=null ? val : 0;
  return '<div class="card">'+label+'<b>'+v+'</b>'+(hint?'<small>'+hint+'</small>':'')+'</div>';
}
function cardPct(label, val, hint){
  return '<div class="card">'+label+'<b class="pct">'+pct(val)+'</b><small>'+hint+'</small></div>';
}
function showAdminErr(msg){
  const el=document.getElementById("admin-err");
  if(!el) return;
  el.style.display="block";
  el.textContent=msg;
}
async function load(){
  if(!token){
    showAdminErr("URL에 ?token= 값이 없습니다. Render ADMIN_TOKEN 과 동일한 값을 붙여 주세요. 예: /admin?token=여기");
    return;
  }
  const kpiUrl = "/api/admin/kpi?token="+encodeURIComponent(token);
  const kr = await fetch(kpiUrl,{headers:h});
  if(!kr.ok){
    const err = await kr.json().catch(()=>({}));
    const hint = kr.status===401 ? "토큰이 Render Environment 의 ADMIN_TOKEN 과 다릅니다." : (err.detail||"");
    showAdminErr("KPI 조회 실패 (HTTP "+kr.status+"). "+hint);
    return;
  }
  document.getElementById("admin-err").style.display="none";
  const k = await kr.json();
  const f = k.funnel || {};
  document.getElementById("funnel-detail").innerHTML =
    card("상세 노출", f.detail_views)+
    card("CTA 클릭", f.detail_cta_clicks)+
    card("간편 진단 완료", f.diagnoses_html_detail, "channel=html_detail")+
    cardPct("클릭 전환율", f.click_rate_pct, "클릭 ÷ 노출")+
    cardPct("넓은 전환율", f.wide_conversion_pct, "진단완료 ÷ 노출")+
    cardPct("클릭→진단", f.diagnosis_after_click_pct, "진단완료 ÷ 클릭");
  document.getElementById("funnel-precision").innerHTML =
    card("정밀 폼 노출", f.precision_form_views)+
    card("발치수 입력 시작", f.precision_input_started)+
    card("정밀 접수 완료", f.precision_completed, "DB precision_completed")+
    card("접수 완료 화면", f.precision_complete_views, "사진 안내 노출")+
    card("폼 이탈(추정)", f.precision_form_dropoff, "폼노출 − 접수완료")+
    cardPct("정밀 제출율", f.precision_submit_rate_pct, "접수완료 ÷ 폼노출")+
    cardPct("입력→제출", f.precision_input_to_submit_pct, "접수완료 ÷ 입력시작")+
    card("앱 사진 업로드", f.precision_photo_app_uploads)+
    cardPct("앱 사진율", f.photo_app_after_precision_pct, "앱업로드 ÷ 정밀접수");
  document.getElementById("funnel-photo").innerHTML =
    card("문자·카카오 수신(누적)", f.photo_received_total, "일별 수기 합계")+
    cardPct("문자 수신율(누적)", f.photo_after_precision_pct, "수기합 ÷ 정밀접수")+
    cardPct("사진 커버리지(참고)", f.photo_combined_after_precision_pct, "앱+수기 ÷ 접수, 중복 가능");
  document.getElementById("photoRows").innerHTML = (f.photo_daily||[]).map(r=>
    '<tr><td>'+r.log_date+'</td><td>'+r.photo_count+'</td><td>'+(r.memo||"")+'</td><td>'+(r.updated_at||"")+'</td></tr>'
  ).join("") || '<tr><td colspan="4">아직 입력 없음</td></tr>';
  const kpiLabels = {
    total_diagnoses:"진단 전체", sf01:"SF01", sf02:"SF02", sf03:"SF03", sf04:"SF04", sf05:"SF05", sf00:"SF00",
    complex_case:"복합", precision_completed:"정밀완료", orders_registered:"주문등록", returns_registered:"반품등록"
  };
  document.getElementById("kpi").innerHTML = Object.entries(k.counts||{}).map(([key,v])=>
    '<div class="card">'+(kpiLabels[key]||key)+'<b>'+v+'</b></div>').join("");
  const c = k.cohort || {};
  const labels = {none:"진단없음", diagnosis_only:"진단만", diagnosis_stretch:"진단+발볼늘림"};
  document.getElementById("cohort").innerHTML = Object.entries(labels).map(([key,label])=>{
    const x = c[key]||{};
    const rate = x.return_rate_pct!=null ? x.return_rate_pct+"%" : "-";
    return '<div class="card">'+label+'<b>'+rate+'</b><small>주문 '+ (x.orders||0) +' / 반품 '+(x.returns||0)+'</small></div>';
  }).join("");
  const listUrl = "/api/admin/diagnoses?token="+encodeURIComponent(token)+"&q="+encodeURIComponent(document.getElementById("q").value||"");
  const lr = await fetch(listUrl,{headers:h});
  if(!lr.ok){ showAdminErr("진단 목록 조회 실패 (HTTP "+lr.status+")"); return; }
  const list = await lr.json();
  document.getElementById("rows").innerHTML = (list.items||[]).map(r=>{
    const photo = r.photo_storage_key
      ? '<a href="/api/admin/diagnoses/'+r.id+'/photo?token='+encodeURIComponent(token)+'" target="_blank" rel="noopener">보기</a>'
      : "-";
    return `<tr>
    <td>${r.diagnosis_code}</td><td>${r.recommendation_code}</td><td>${r.q4||""}</td>
    <td>${photo}</td>
    <td><input data-id="${r.id}" class="order" value="${r.order_no||""}"/></td>
    <td><select data-id="${r.id}" class="ret"><option value="0" ${r.return_status==0?"selected":""}>N</option><option value="1" ${r.return_status==1?"selected":""}>Y</option></select></td>
    <td><select data-id="${r.id}" class="work"><option value="">-</option><option value="1" ${r.actual_work_step==1?"selected":""}>1단계</option><option value="2" ${r.actual_work_step==2?"selected":""}>2단계</option></select></td>
    <td><button data-id="${r.id}" class="save">저장</button></td></tr>`;
  }).join("");
  document.querySelectorAll(".save").forEach(b=>b.onclick=async()=>{
    const id=b.dataset.id;
    await fetch("/api/admin/diagnoses/"+id,{method:"PATCH",headers:{...h,"Content-Type":"application/json"},
      body:JSON.stringify({order_no:document.querySelector('.order[data-id="'+id+'"]').value,
        return_status:+document.querySelector('.ret[data-id="'+id+'"]').value,
        actual_work_step:document.querySelector('.work[data-id="'+id+'"]').value||null})});
    load();
  });
}
document.getElementById("search").onclick=load;
document.getElementById("savePhoto").onclick=async()=>{
  const d=document.getElementById("photoDate").value;
  const n=document.getElementById("photoCount").value;
  if(!d){ alert("날짜를 선택하세요."); return; }
  const res=await fetch("/api/admin/photo-daily",{method:"PUT",headers:{...h,"Content-Type":"application/json"},
    body:JSON.stringify({log_date:d, photo_count:+(n||0), memo:document.getElementById("photoMemo").value||""})});
  if(!res.ok){ const e=await res.json().catch(()=>({})); alert(e.detail||"저장 실패"); return; }
  document.getElementById("photoMemo").value="";
  load();
};
document.getElementById("addOrder").onclick=async()=>{
  await fetch("/api/admin/orders/no-diagnosis",{method:"POST",headers:{...h,"Content-Type":"application/json"},
    body:JSON.stringify({order_no:document.getElementById("ono").value, return_status:+document.getElementById("ret").value})});
  load();
};
load();
(function(){ const el=document.getElementById("photoDate"); if(el){ el.value=new Date().toISOString().slice(0,10); }})();
</script></body></html>"""

PILOT_BUILD = "20260611-pilot-short-s"
