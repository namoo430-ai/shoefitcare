"""파일럿 / 관리자 HTML (FastAPI에서 로드)."""

from pilot_copy import PILOT_COPY_VERSION, dump_pilot_copy_json

PILOT_COPY_JSON = dump_pilot_copy_json()

PILOT_HTML = """<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css"/>
<title>Every Fit · 내 발에 맞는 핏 찾기</title>
<style>
:root{--brand:#e03d5c;--brand-soft:#fff1f4;--brand-border:#f7c9d4;--brand-ring:rgba(224,61,92,.28);--pink:var(--brand);--point-red:var(--brand);--ink:var(--text);--bg:#f2f2f7;--card:#fff;--muted:#6b7280;--border:#e5e5ea;--text:#1c1c1e;--radius-card:18px;--radius-control:14px;--radius-pill:999px;--shadow-card:0 1px 3px rgba(0,0,0,.05);--shadow-choice:0 1px 4px rgba(0,0,0,.06)}
body{margin:0;font-size:16px;font-family:"Pretendard",-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased;font-weight:400}
.wrap{max-width:430px;margin:0 auto;padding:12px 14px 80px}
.card{background:var(--card);border-radius:var(--radius-card);padding:16px;margin:10px 0;border:1px solid var(--border);box-shadow:var(--shadow-card)}
h1{font-size:18px;margin:0 0 6px;font-weight:700;line-height:1.4;letter-spacing:-0.02em}
h2.prec-h2{font-size:17px;margin:0 0 8px;font-weight:700;line-height:1.4}
p.sub{color:var(--muted);font-size:16px;line-height:1.6;margin:0;font-weight:400}
.pilot-step-brand{margin:0 0 8px;font-size:13px;font-weight:600;letter-spacing:0.16em;text-transform:uppercase;color:var(--brand);text-align:center}
.step-progress{font-size:15px;color:var(--pink);margin:0 0 10px;font-weight:600}
#step h1{line-height:1.45;margin:0 0 12px}
#step .sub{margin:0 0 16px}
.step-choices{display:flex;flex-direction:column;gap:10px}
.step-choices .btn{margin:0;line-height:1.5;padding:14px 12px}
.chips-row{display:flex;flex-wrap:wrap;gap:10px}
.chips-col{display:flex;flex-direction:column;gap:10px}
.chips-size-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;width:100%}
.chips-size-grid .chip{display:flex;align-items:center;justify-content:center;padding:8px 6px;min-height:0;width:100%;margin:0;text-align:center;box-sizing:border-box;line-height:1.2;font-family:inherit;-webkit-tap-highlight-color:transparent;touch-action:manipulation}
.chips-row .chip.on,.chips-col .chip.on,.chips-size-grid .chip.on{background:var(--pink);color:#fff;border-color:var(--pink);font-weight:700;box-shadow:none}
.cta-wrap{margin-top:24px;padding-top:20px;border-top:1px solid #e8e8ed}
.cta-wrap .btn.primary{margin:0}
.btn-step-back{display:block;width:100%;margin:12px 0 0;padding:12px;border-radius:var(--radius-control);border:1px solid var(--border);background:#fff;color:var(--muted);font-size:16px;font-weight:500;cursor:pointer;text-align:center;font-family:inherit;box-shadow:none;-webkit-tap-highlight-color:transparent;touch-action:manipulation;min-height:44px}
.btn-step-back:active{background:#f9f9fb}
.btn{display:block;width:100%;margin:6px 0;padding:14px 12px 14px 14px;border-radius:var(--radius-control);border:1px solid var(--border);background:#fff;font-size:16px;cursor:pointer;text-align:left;line-height:1.5;transition:border-color .15s,background .15s;-webkit-tap-highlight-color:transparent;touch-action:manipulation;box-shadow:none}
.step-choices .btn{margin:0}
.step-choices .btn.on{position:relative;border-color:var(--pink);background:var(--brand-soft);color:var(--pink);font-weight:700;box-shadow:none}
.step-choices .btn.on::before{content:"✓";position:absolute;left:12px;top:50%;transform:translateY(-50%);font-size:17px;font-weight:700;color:var(--pink)}
.step-choices .btn.on{padding-left:38px}
.btn.primary{background:var(--pink);color:#fff;border:0;text-align:center;font-weight:600;border-radius:var(--radius-pill);min-height:48px;padding:14px 20px;box-shadow:none;-webkit-tap-highlight-color:transparent;touch-action:manipulation}
.btn.primary:active{opacity:.92}
.chip{padding:10px 14px;border-radius:var(--radius-control);border:1px solid var(--border);background:#fff;font-size:16px;cursor:pointer;line-height:1.45;transition:border-color .15s,background .15s;box-shadow:none;-webkit-tap-highlight-color:transparent;touch-action:manipulation}
.chips-col .chip{display:block;width:100%;text-align:left;padding:12px 14px;line-height:1.5;box-sizing:border-box;border-radius:12px}
.hidden{display:none}
.result-msg{white-space:pre-wrap;font-size:16px;line-height:1.55;margin:0 0 10px;font-family:inherit;color:inherit}
.result-dx{margin:12px 0 8px;font-size:16px}
.result-hint{margin:6px 0;line-height:1.55;font-size:16px}
.result-footnote{margin:14px 0 0;font-size:15px;color:var(--muted);line-height:1.5;text-align:center}
.coupang-steps{margin:16px 0;padding:14px;border-radius:12px;background:#fff;border:1px solid var(--border);font-size:16px;line-height:1.55}
.coupang-steps ol{margin:8px 0 0;padding-left:20px}
.coupang-steps li{margin:6px 0}
.btn-inquiry-short{margin-top:10px}
.btn-inquiry-long{margin-top:8px;background:#fff;color:var(--pink);border:1px solid var(--pink)}
.fit-ux{margin:14px 0;padding:12px 14px;border-radius:12px;background:#f8fafc;border:1px solid var(--border);font-size:16px;line-height:1.5}
.fit-ux b{font-size:21px;color:var(--pink)}
.fit-trust-low{margin-top:8px;font-size:15px;color:#92400e}
.result-cta{margin-top:12px;padding-top:0;border-top:0}
.result-next-wrap{margin-top:20px;padding-top:18px;border-top:1px solid #e8e8ed}
.result-next-hint{font-size:15px;color:var(--muted);line-height:1.5;margin:0 0 12px;text-align:center}
.btn-result-next{display:block;width:100%;padding:14px 12px;border-radius:var(--radius-pill);border:1px solid var(--pink);background:#fff;color:var(--pink);font-size:16px;font-weight:600;cursor:pointer;text-align:center;font-family:inherit;line-height:1.45;min-height:48px;box-sizing:border-box}
.btn-result-next:active{background:var(--brand-soft)}
.result-detail-back-wrap{margin-top:20px;padding-top:4px}
.result-detail-back-wrap .result-back-hint{font-size:15px;color:var(--muted);line-height:1.5;margin:0 0 12px;text-align:center}
.prec-step-head{margin:0 0 16px}
.prec-step-head h2{font-size:17px;margin:0 0 8px;line-height:1.45;font-weight:700}
.prec-step-head p{font-size:16px;line-height:1.55;color:var(--muted);margin:0}
input{width:100%;padding:11px 12px;border-radius:10px;border:1px solid var(--border);margin:0;font-size:16px;box-sizing:border-box;background:#fff;color:var(--text)}
label.field-label{display:block;font-size:15px;color:var(--muted);margin:0 0 6px;font-weight:500}
.prec-block{border:1px solid var(--border);border-radius:12px;padding:14px;margin:0 0 12px;background:#fafafa}
.prec-block-title{font-size:16px;font-weight:700;margin:0 0 12px;display:flex;align-items:center;gap:6px}
.prec-field{margin:0 0 12px}
.prec-field:last-child{margin-bottom:0}
.prec-section{margin:0 0 12px}
.prec-section-title{font-size:16px;font-weight:700;margin:0 0 4px;display:flex;align-items:center;gap:6px}
.prec-section-note{font-size:15px;color:var(--muted);margin:0 0 10px;line-height:1.45}
.prec-photo{border:1px solid var(--border);border-radius:12px;padding:14px;margin:16px 0;background:#fff}
.prec-photo p{font-size:16px;line-height:1.55;margin:0 0 8px;color:var(--text)}
.prec-photo-alt{font-size:15px;color:var(--muted);line-height:1.5;margin:10px 0 0}
.prec-photo-preview{display:block;max-width:100%;max-height:160px;margin:10px auto 0;border-radius:8px}
.prec-photo-file{width:100%;font-size:16px;margin-top:8px}
.prec-phone{font-size:16px;font-weight:700;letter-spacing:0.02em;margin:0}
.prec-consent{display:flex;align-items:flex-start;gap:8px;margin:12px 0 0;font-size:15px;line-height:1.45;color:var(--text)}
.prec-consent input[type=checkbox]{width:18px;height:18px;margin:2px 0 0;flex-shrink:0}
.btn-prec-submit{display:flex;align-items:center;justify-content:center;box-sizing:border-box;margin-top:8px;border-radius:var(--radius-pill);padding:14px;font-size:17px;font-weight:600;background:var(--pink);color:#fff;border:0;width:100%;min-height:48px;cursor:pointer;text-align:center;font-family:inherit;box-shadow:none;-webkit-tap-highlight-color:transparent;touch-action:manipulation}
.prec-done-title{font-size:18px;font-weight:700;margin:0 0 14px;line-height:1.45}
.prec-done p{font-size:16px;line-height:1.6;margin:0 0 12px;color:var(--text)}
.prec-done p:last-of-type{margin-bottom:20px}
.btn-detail-back{display:block;width:100%;text-align:center;text-decoration:none;border-radius:var(--radius-pill);padding:14px;font-size:16px;font-weight:600;background:#fff;color:var(--pink);border:1px solid var(--pink);cursor:pointer;box-sizing:border-box;min-height:48px}
.progress-bar{height:8px;background:#ececf0;border-radius:var(--radius-pill);margin:0 0 10px;overflow:hidden}
.progress-bar>i{display:block;height:100%;background:var(--pink);border-radius:99px;transition:width .25s}
.step-split{display:flex;flex-direction:column;gap:12px;align-items:center;width:100%}
#step.pilot-q2-step{display:flex;flex-direction:column;align-items:center;text-align:center}
#step.pilot-q2-step .pilot-step-brand,#step.pilot-q2-step .progress-bar,#step.pilot-q2-step h1,#step.pilot-q2-step .sub,#step.pilot-q2-step .q2-step,#step.pilot-q2-step .cta-wrap{width:100%;max-width:360px;box-sizing:border-box}
#step.pilot-q2-step .sub{position:relative;z-index:12;margin:0 0 18px;padding-bottom:6px;background:var(--card)}
.map-sticky{position:sticky;top:0;z-index:2;background:var(--card);padding:8px 0 4px;border-bottom:1px solid #f0f0f2;margin:0 0 4px}
.map-caption{font-size:14px;color:var(--muted);text-align:center;margin:6px 0 0;line-height:1.4}
.foot-map{width:100%;max-width:200px;margin:0 auto;display:block}
.foot-map.foot-map-lg{max-width:260px}
.foot-map .sole{fill:#f3f4f6;stroke:#d1d5db;stroke-width:1.2}
.foot-map .zone{fill:var(--pink);opacity:0;transition:opacity .2s}
.foot-map .zone.on{opacity:.35}
.foot-map .zone.lv2{opacity:.45}
.foot-map .zone.lv3{opacity:.58}
.foot-map .zone.lv4{opacity:.72}
.foot-map .zone.comfort{opacity:.22;fill:#86efac}
.foot-map.q2-interactive .zone{opacity:.14;cursor:pointer;pointer-events:all;-webkit-tap-highlight-color:transparent;touch-action:manipulation}
.foot-map.q2-interactive .zone.on{opacity:.52}
.foot-map.q2-interactive .zone:focus{outline:2px solid var(--brand);outline-offset:2px}
.q2-step .q2-map-wrap{margin:0 auto;max-width:min(420px,100%);padding:0;width:100%}
.q2-map-stack{margin-bottom:0;display:flex;flex-direction:column;align-items:center;width:100%}
.q2-step .map-caption{font-size:14px;color:var(--muted);text-align:center;margin:6px 0 4px;line-height:1.4;word-break:keep-all}
.q2-foot-stage{position:relative;width:100%;max-width:200px;margin:0 auto;aspect-ratio:272/300;max-height:min(34vh,200px)}
.q2-foot-photo{width:100%;height:100%;object-fit:contain;display:block;pointer-events:none;user-select:none}
.q2-hotspot-layer{position:absolute;inset:0;pointer-events:none}
.q2-hotspot{position:absolute;transform:translate(-50%,-50%);border:0;background:transparent;padding:0;margin:0;cursor:pointer;touch-action:manipulation;pointer-events:all;-webkit-tap-highlight-color:transparent}
.q2-hotspot-map{max-width:none}
.q2-map-pin{display:flex;flex-direction:column;align-items:center;gap:3px}
.q2-hotspot-row{display:flex;flex-direction:row;align-items:center;gap:5px;max-width:100%}
.q2-dot{width:14px;height:14px;border-radius:50%;background:#facc15;box-shadow:0 0 0 1.5px rgba(0,0,0,.12);flex-shrink:0}
.q2-hotspot.on .q2-dot{background:#f59e0b;box-shadow:0 0 0 3px rgba(224,61,92,.35)}
.q2-num-badge{flex-shrink:0;width:18px;height:18px;border-radius:50%;background:#dc2626;color:#fff;font-size:13px;font-weight:700;line-height:18px;text-align:center;box-shadow:0 0 0 1px rgba(255,255,255,.85)}
.q2-hotspot.on .q2-num-badge{background:#b91c1c;box-shadow:0 0 0 2px rgba(224,61,92,.35)}
.q2-legend{display:grid;grid-template-columns:1fr 1fr;column-gap:10px;row-gap:2px;margin:8px 0 0;padding:0 4px;border:0;background:transparent;width:100%;max-width:360px;box-sizing:border-box}
.q2-foot-panel{width:100%;position:relative;z-index:1;margin-bottom:0;display:flex;flex-direction:column;align-items:center}
.q2-legend-item{display:flex;align-items:center;gap:6px;width:100%;border:0;background:transparent;padding:6px 2px;cursor:pointer;text-align:left;font-family:inherit;border-radius:0;box-sizing:border-box;touch-action:manipulation;-webkit-tap-highlight-color:transparent}
.q2-legend-item.on .q2-legend-label{color:var(--brand)}
.q2-legend-item.q2-legend-none{grid-column:1 / -1;margin-top:2px;padding:8px 4px;border-radius:10px;border:1px solid var(--border);justify-content:center}
.q2-legend-item.q2-legend-none.on{border-color:var(--brand);background:rgba(224,61,92,.08)}
.q2-legend-label{font-size:15px;font-weight:600;color:var(--text);line-height:1.35;word-break:keep-all}
#step.pilot-q2-step .cta-wrap{position:sticky;bottom:0;z-index:20;margin-top:8px;padding:10px 0 max(10px,env(safe-area-inset-bottom));background:linear-gradient(180deg,rgba(255,255,255,0) 0%,#fff 28%);width:100%;max-width:360px;box-sizing:border-box}
body.senior-ux .q2-legend-label{font-size:16px}
body.senior-ux .q2-num-badge{width:20px;height:20px;font-size:14px;line-height:20px}
body.senior-ux .q2-dot{width:16px;height:16px}
.result-head{font-size:18px;font-weight:700;margin:0 0 12px;line-height:1.45;color:var(--text)}
.comfort-bars{margin:16px 0;padding:14px;border-radius:12px;background:#fafafa;border:1px solid var(--border)}
.comfort-bars h3{font-size:15px;font-weight:600;margin:0 0 10px;color:var(--point-red);line-height:1.35}
.comfort-row{display:flex;align-items:center;gap:10px;margin:0 0 10px;font-size:15px;line-height:1.35}
.comfort-row:last-child{margin-bottom:0}
.comfort-row span.lbl{flex:1;min-width:0}
.comfort-dots{display:flex;gap:4px;flex-shrink:0}
.comfort-dots i{width:22px;height:8px;border-radius:4px;background:#e5e7eb;display:block}
.comfort-dots i.on{background:var(--point-red)}
.comfort-hint{font-size:14px;color:var(--muted);margin:10px 0 0;line-height:1.45}
.result-dx.naver-hide{display:none}
.map-legend{font-size:14px;color:var(--muted);text-align:center;margin:8px 0 0}
#step:empty{display:none}
.intro-line{font-size:16px;color:var(--muted);line-height:1.55;margin:0 0 14px}
.build-tag{font-size:13px;color:var(--pink);margin:12px 0 0}
.intro-hero{display:flex;flex-direction:column;justify-content:center;align-items:center;min-height:100dvh;text-align:center;padding:max(6vh,32px) 16px max(20px,env(safe-area-inset-bottom));box-sizing:border-box;gap:0}
body.intro-screen{background:#fff}
body.intro-screen .wrap{background:#fff;padding:0;max-width:100%;min-height:100dvh;overflow-y:auto;-webkit-overflow-scrolling:touch}
#step.intro-step.card{background:#fff;border:0;box-shadow:none;padding:0;margin:0;min-height:min(100dvh,100%)}
.intro-head{position:relative;z-index:2;width:100%;max-width:360px;flex-shrink:0;margin:0 0 2px}
.intro-brand{margin:0 0 12px;font-size:14px;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;color:var(--brand)}
.intro-hero h1{font-size:20px;line-height:1.45;margin:0;font-weight:700;letter-spacing:-0.02em;color:var(--text)}
.intro-visual{display:flex;flex-direction:column;align-items:center;width:100%;flex:0 0 auto;margin:-24px 0 0;position:relative;z-index:1}
.intro-img-frame{display:flex;align-items:flex-end;justify-content:center;margin:0;width:100%;line-height:0}
.intro-foot-stage{position:relative;width:100%;max-width:272px;height:248px;display:flex;align-items:flex-end;justify-content:center}
.intro-foot-stage img.intro-foot-img{width:100%;max-width:272px;height:238px;object-fit:contain;display:block;padding:0;vertical-align:bottom}
.intro-tagline{position:absolute;left:0;right:0;bottom:16px;margin:0;padding:0 10px;font-size:16px;font-weight:500;color:var(--muted);letter-spacing:0.02em;line-height:1.2;text-align:center;z-index:2;pointer-events:none}
.intro-build{font-size:12px;color:var(--muted);margin:2px 0 0;opacity:.85}
.intro-hero .cta-wrap{margin-top:14px;padding-top:0;border-top:0;width:100%;display:flex;justify-content:center;box-sizing:border-box}
.intro-hero .cta-wrap .btn.primary{width:auto;display:inline-block;max-width:calc(100% - 28px);padding:14px 22px;margin:0;white-space:nowrap;border-radius:var(--radius-pill)}
.foot-compare-block{margin:0 0 16px;padding:0}
.foot-compare-card{border:1px solid var(--border);border-radius:var(--radius-control);overflow:hidden;background:#fff;box-shadow:var(--shadow-card)}
.foot-compare-head{padding:12px 14px;background:#fafafa;border-bottom:1px solid var(--border)}
.foot-compare-body{background:#fff}
.foot-compare-stack{display:flex;flex-direction:column;border:0;border-radius:0;overflow:hidden;background:#fff}
.foot-compare-tier{padding:10px 8px;background:#fff}
.foot-compare-tier--cust{border-top:1px solid #e8e8ed}
.foot-compare-spec-title{font-size:15px;font-weight:700;color:var(--text);margin:0 0 8px;text-align:left;line-height:1.35}
.foot-compare-row{display:flex;flex-direction:row;gap:8px;align-items:center;min-height:178px}
.foot-compare-img-cell{flex:0 0 52%;max-width:196px;height:178px;display:flex;align-items:center;justify-content:center;position:relative;background:transparent;border-radius:8px;border:0;box-sizing:border-box;padding:0;overflow:hidden}
.foot-compare-img-stage{position:relative;width:100%;height:100%;transform:scale(1.48);transform-origin:center center}
.foot-compare-img-stage img{width:100%;height:100%;object-fit:contain;display:block;padding:0;box-sizing:border-box}
.foot-compare-spec-list{flex:1 1 50%;min-width:0;display:flex;flex-direction:column;justify-content:center;gap:5px;padding:0 4px 0 6px;box-sizing:border-box}
.foot-spec-line{margin:0;font-size:15px;line-height:1.5;color:var(--text);text-align:left;word-break:keep-all;overflow-wrap:break-word}
.pain-dot{position:absolute;width:7px;height:7px;margin:-3.5px 0 0 -3.5px;border-radius:50%;background:#ef4444;box-shadow:0 0 0 1px rgba(255,255,255,.9);animation:pain-dot-blink .85s ease-in-out infinite}
@keyframes pain-dot-blink{0%,100%{opacity:.35}50%{opacity:1}}
@media (prefers-reduced-motion: reduce){.pain-dot{animation:none;opacity:.9}}
.foot-compare-note{font-size:13px;color:var(--muted);margin:10px 4px 0;line-height:1.45;text-align:left;word-break:keep-all;overflow-wrap:break-word;padding:0 10px}
@media (prefers-reduced-motion: reduce){.intro-foot-img{transition:none}}
body.senior-ux{font-size:19px}
body.senior-ux h1{font-size:21px}
body.senior-ux #step h1{font-size:20px}
body.senior-ux .btn,body.senior-ux .chip{min-height:48px;font-size:18px;padding-top:14px;padding-bottom:14px}
body.senior-ux .chips-size-grid .chip{min-height:44px;padding:10px 6px}
body.senior-ux .btn.primary{font-size:18px;padding:16px 12px}
body.senior-ux .intro-line,body.senior-ux p.sub{font-size:17px}
.foot-type-block{margin:14px 0;padding:14px;border-radius:12px;background:#f8fafc;border:1px solid var(--border);font-size:16px;line-height:1.55}
.foot-type-block p{margin:0 0 6px;word-break:keep-all;overflow-wrap:break-word;text-align:left}
.foot-type-block p:last-child{margin-bottom:0}
.result-sec-title{font-size:15px;font-weight:600;margin:0 0 10px;color:var(--point-red);line-height:1.35;word-break:keep-all}
.foot-compare-head .foot-compare-block-title{font-size:15px;font-weight:600;margin:0;color:var(--point-red);line-height:1.35}
.fit-lines-block{margin:14px 0;padding:14px;border-radius:12px;background:#fafafa;border:1px solid var(--border)}
.fit-line-row{display:flex;align-items:center;gap:8px;margin:0 0 8px;font-size:15px}
.fit-line-row.rec .fit-name{font-weight:700;color:var(--point-red)}
.fit-line-row .fit-name{flex:0 0 88px}
.order-tip-box{margin:14px 0;padding:14px;border-radius:12px;background:var(--brand-soft);border:1px solid var(--brand-border);font-size:16px;line-height:1.5}
.order-tip-box .tip-box-title{font-size:15px;font-weight:600;margin:0 0 8px;color:var(--point-red)}
.order-tip-box .alt{font-size:15px;color:var(--muted);margin:8px 0 0}
.exchange-block{margin:18px 0 8px}
.exchange-card{background:#fff;border:1px solid var(--border);border-radius:var(--radius-control);overflow:hidden;box-shadow:var(--shadow-card)}
.exchange-head{padding:12px 14px;background:#fff;border-bottom:1px solid var(--border)}
.exchange-head .tip-box-title{margin:0;font-size:15px;font-weight:600;color:var(--point-red);line-height:1.35}
.exchange-body-bg{padding:10px 14px 4px;background:#fafafa;font-size:15px;line-height:1.5;color:var(--ink);font-weight:400}
.exchange-body-bg p{margin:0 0 8px;padding:0}
.exchange-body-bg p:last-child{margin-bottom:0}
.exchange-body-bg .sub{font-size:14px;color:var(--muted);line-height:1.45;font-weight:400}
.exchange-actions{display:flex;flex-direction:column;gap:10px;padding:16px 14px 14px;background:#fff;margin:0;border-top:1px solid #ececf0}
.exchange-actions .btn{width:100%;margin:0;box-sizing:border-box;text-align:center;font-family:inherit;font-size:17px;font-weight:600;padding:14px;border-radius:var(--radius-pill);border:0;cursor:pointer;min-height:48px;box-shadow:none;-webkit-tap-highlight-color:transparent;touch-action:manipulation}
.exchange-actions .btn.primary{background:var(--pink);color:#fff;box-shadow:none}
.exchange-actions .btn.secondary{background:#f1f5f9;color:#0f172a}
.exchange-actions .btn:disabled{opacity:.42;cursor:not-allowed}
.order-tip-box .stretch-prec-note{font-size:15px;color:#64748b;line-height:1.5}
.tip-guide-block{margin:14px 0;border-radius:var(--radius-control);background:#fff;border:1px solid var(--border);overflow:hidden;box-shadow:var(--shadow-card)}
.tip-guide-block--nohead .tip-guide-row:first-child{border-top:0}
.tip-guide-block h3{font-size:15px;font-weight:600;margin:0;padding:12px 12px 8px;color:var(--muted)}
.tip-guide-row{display:flex;align-items:center;gap:10px;width:100%;margin:0;padding:14px 12px;border:0;border-top:1px solid var(--brand-border);background:var(--brand-soft);text-align:left;font-family:inherit;font-size:15px;line-height:1.4;cursor:pointer;color:var(--ink);box-shadow:none;-webkit-tap-highlight-color:transparent;touch-action:manipulation}
.tip-guide-block h3+.tip-guide-row{border-top:0}
.tip-guide-row .tip-row-title{flex:0 0 auto;font-weight:600;font-size:15px;color:var(--point-red);max-width:40%}
.tip-guide-row .tip-row-summary{flex:1;min-width:0;color:#475569;font-size:14px;line-height:1.45;word-break:keep-all;overflow-wrap:break-word;font-weight:400}
.tip-guide-row .tip-row-chevron{flex:0 0 auto;color:#94a3b8;font-size:19px;line-height:1}
body.senior-ux .tip-guide-row{min-height:52px}
body.senior-ux .tip-guide-row .tip-row-title{font-size:16px}
body.senior-ux .tip-guide-row .tip-row-summary{font-size:15px}
.pilot-sheet .sheet-body-tip{font-size:16px;line-height:1.55;margin:0 0 12px;color:var(--ink)}
body.has-bottom-bar .wrap{padding-bottom:72px}
.pilot-bottom-bar{position:fixed;left:0;right:0;bottom:0;z-index:40;max-width:430px;margin:0 auto;display:flex;background:#fff;border-top:1px solid #e2e8f0;box-shadow:0 -4px 16px rgba(0,0,0,.06)}
.pilot-bottom-bar.hidden{display:none}
.pilot-bottom-bar button{flex:1;padding:12px 6px;border:0;background:transparent;font-size:14px;font-weight:600;color:#475569;cursor:pointer;font-family:inherit;box-shadow:none;-webkit-tap-highlight-color:transparent;touch-action:manipulation;min-height:48px}
.pilot-bottom-bar button:disabled{opacity:.35;cursor:not-allowed}
.pilot-bottom-bar button.primary-tab{color:var(--pink)}
.pilot-sheet-backdrop{position:fixed;inset:0;background:rgba(0,0,0,.35);z-index:50;display:flex;align-items:flex-end;justify-content:center}
.pilot-sheet-backdrop.hidden{display:none}
.pilot-sheet{width:100%;max-width:430px;background:#fff;border-radius:16px 16px 0 0;padding:16px 16px 24px;max-height:85vh;overflow:auto}
.pilot-sheet h2{font-size:18px;margin:0 0 12px}
.pilot-sheet .sheet-preview{background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:12px;font-size:15px;line-height:1.5;white-space:pre-wrap;margin:0 0 12px}
.pilot-sheet .sheet-hints{font-size:15px;color:#64748b;line-height:1.5;margin:0 0 14px;padding-left:18px}
.pilot-sheet .sheet-hints li{margin:4px 0}
.pilot-sheet .sheet-actions{display:flex;flex-direction:column;gap:10px}
.pilot-sheet .btn-sheet{padding:14px;border-radius:var(--radius-pill);border:0;font-size:16px;font-weight:600;cursor:pointer;font-family:inherit;min-height:48px;box-shadow:none;-webkit-tap-highlight-color:transparent;touch-action:manipulation}
.pilot-sheet .btn-sheet.primary{background:var(--pink);color:#fff}
.pilot-sheet .btn-sheet.secondary{background:#f1f5f9;color:#0f172a}
.pilot-sheet .fit-cat-btn{display:block;width:100%;text-align:left;padding:12px 14px;margin:0 0 8px;border-radius:10px;border:1px solid #e2e8f0;background:#fff;font-size:16px;cursor:pointer;font-family:inherit}
.pilot-sheet .fit-cat-btn.rec{border-color:var(--brand);background:var(--brand-soft);font-weight:700}
.pilot-sheet .sheet-close{margin-top:12px;width:100%;padding:12px;border:0;background:transparent;color:#64748b;font-size:16px;cursor:pointer}
</style><!-- pilot-build: __PILOT_BUILD__ --></head><body>
<div class="wrap">
  <div id="step" class="card"></div>
  <div id="result" class="card hidden"></div>
  <div id="prec-teaser" class="card hidden prec-teaser"></div>
  <div id="precision" class="card hidden"></div>
</div>
<nav id="pilot-bottom-bar" class="pilot-bottom-bar hidden" aria-label="결과 메뉴">
  <button type="button" id="tab-talk" disabled>톡톡문의</button>
  <button type="button" id="tab-fit" disabled>핏별상품</button>
  <button type="button" id="tab-prec" disabled>정밀진단</button>
</nav>
<div id="pilot-sheet-backdrop" class="pilot-sheet-backdrop hidden" aria-hidden="true">
  <div class="pilot-sheet" id="pilot-sheet" role="dialog"></div>
</div>
<script>
const PILOT_COPY = __PILOT_COPY_JSON__;
const sizes = [225,230,235,240,245,250,255];
const params = new URLSearchParams(location.search);
const productId = params.get("product_id") || "";
const src = params.get("src") || "web";
const returnUrl = (params.get("return_url") || params.get("order_url") || "").trim();
const coupangChannel = /^coupang/i.test(src);
const naverChannel = /^naver/i.test(src);
const seniorUx = naverChannel || (params.get("ux") || "").toLowerCase() === "senior";
if(seniorUx){ document.body.classList.add("senior-ux"); }
function productDetailHref(){
  const q = productId ? "?product_id="+encodeURIComponent(productId) : "";
  return location.origin+"/product-detail"+q;
}
function orderPageHref(){
  if(returnUrl) return returnUrl;
  if(coupangChannel || naverChannel) return "";
  return productDetailHref();
}
function orderBackLabel(){
  if(returnUrl || coupangChannel) return "쿠팡에서 주문하기";
  if(naverChannel) return "스마트스토어에서 주문하기";
  return "주문 페이지로 돌아가기";
}
function orderBackHint(recommendationCode){
  if(returnUrl || coupangChannel){
    return recommendationCode==="SF00"
      ? '<p class="result-back-hint">안내 확인 후 아래 버튼으로 <b>쿠팡 상품 페이지</b>에서 사이즈를 선택해 주문해 주세요.</p>'
      : '<p class="result-back-hint">발볼 안내·문의 후 주문하시려면 <b>쿠팡 상품 페이지</b>로 돌아가 주세요.</p>';
  }
  if(naverChannel){
    return recommendationCode==="SF00"
      ? '<p class="result-back-hint">안내 확인 후 <b>네이버 스마트스토어 상품 페이지</b>에서 사이즈를 선택해 주문해 주세요.</p>'
      : '<p class="result-back-hint">발볼 안내·문의 후 주문하시려면 <b>스마트스토어 상품 페이지</b>로 돌아가 주세요.</p>';
  }
  return recommendationCode==="SF00"
    ? '<p class="result-back-hint">안내를 확인하신 뒤, 아래 버튼으로 주문 페이지에서 사이즈를 선택해 주세요.</p>'
    : "";
}
function resultDetailBackHtml(recommendationCode){
  const href = orderPageHref();
  if(naverChannel){
    if(href){
      return '<div class="result-detail-back-wrap"><a class="btn-detail-back" href="'+href+'" rel="noopener">'+orderBackLabel()+'</a></div>';
    }
    return "";
  }
  const hint = orderBackHint(recommendationCode);
  if(!href){
    const appHint = coupangChannel
      ? '<p class="result-back-hint">쿠팡 앱으로 돌아가 상품 페이지에서 주문해 주세요.</p>'
      : '';
    return '<div class="result-detail-back-wrap">'+hint+appHint+'</div>';
  }
  return '<div class="result-detail-back-wrap">'+hint
    +'<a class="btn-detail-back" href="'+href+'" rel="noopener">'+orderBackLabel()+'</a></div>';
}
function shouldHideEngineMessage(data){
  return !!naverChannel;
}
function resultMessageHtml(data){
  if(shouldHideEngineMessage(data)) return "";
  const msg = data.message || "";
  if(!msg) return "";
  return '<div class="result-msg">'+escHtml(msg)+'</div>';
}
let diagnosisId = "";
function safeSessionGet(key){
  try { return sessionStorage.getItem(key); } catch(_) { return null; }
}
function safeSessionSet(key, value){
  try { sessionStorage.setItem(key, value); } catch(_) {}
}
function postPilotFunnelEvent(eventName, dxId){
  const body = {event:eventName, product_id:productId||null, channel:src};
  const id = dxId || diagnosisId;
  if(id) body.diagnosis_id = id;
  fetch("/pilot/event",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify(body), keepalive:true}).catch(()=>{});
}
(function(){
  const k = "sf_pilot_land:"+(src||"web")+":"+(productId||"_");
  if(safeSessionGet(k)) return;
  safeSessionSet(k,"1");
  postPilotFunnelEvent("pilot_landing");
})();
let answers = { q1:"", q2:[], q3:"", q4:235 };
let step = 0;
let introActive = true;
let introIndex = 0;
let introTimer = null;
let submitInFlight = false;
const FOOT_IMG_BASE = "/product-images";
const FOOT_INTRO_TYPES = [
  {key:"nomal",label:"보통발",file:"nomal.jpg"},
  {key:"wide",label:"넓은발",file:"wide.jpg"},
  {key:"narrow",label:"좁은발",file:"narrow.jpg"},
  {key:"bunion",label:"무지외반",file:"Bunion.jpg"}
];
const Q1_SLIP = PILOT_COPY.engine_keys.q1_slip;
const Q1_LOOSE = PILOT_COPY.engine_keys.q1_loose;
const Q1_NONE = PILOT_COPY.engine_keys.q1_none;
const FOOT_TYPE_FILES = {nomal:"nomal.jpg",wide:"wide.jpg",narrow:"narrow.jpg",bunion:"Bunion.jpg",slender:"narrow.jpg"};
function activeQ2List(q2){
  const list = Array.isArray(q2) ? q2.filter(x=>x&&String(x).trim()) : [];
  if(!list.length || (list.length===1 && list[0]===Q2_NONE)) return [];
  return list.filter(x=>x!==Q2_NONE);
}
function footCustomerTypeKey(data){
  const fp = data.foot_profile || {};
  const p = String(fp.p_code||"P0").toUpperCase();
  if(p==="P1") return "bunion";
  const q1 = data.q1||"";
  if(q1===Q1_LOOSE) return "slender";
  const r = String(fp.r_code||"R1").toUpperCase();
  if(r==="R2"||r==="R5") return "wide";
  if(r==="R3") return "narrow";
  return "nomal";
}
function footCustomerImageKey(data){
  const fp = data.foot_profile || {};
  const p = String(fp.p_code||"P0").toUpperCase();
  const r = String(fp.r_code||"R1").toUpperCase();
  const q2 = activeQ2List(data.q2 || (data.foot_compare && data.foot_compare.q2) || []);
  const hasHallux = p==="P1" || q2.includes(Q2_HALLUX) || q2.includes(Q2_INDEX);
  const hasBall = q2.includes(Q2_BALL);
  const isWideR = r==="R2"||r==="R5";
  if(hasBall) return "wide";
  if(hasHallux) return "bunion";
  if(isWideR) return "wide";
  return footCustomerTypeKey(data);
}
function footImgFileNormalized(file){
  const f = String(file||"").trim();
  if(!f) return "nomal.jpg";
  if(f.toLowerCase()==="slender.jpg") return "narrow.jpg";
  return f;
}
function footCustomerImageFile(data){
  const key = footCustomerImageKey(data);
  return footImgFileNormalized(FOOT_TYPE_FILES[key]||FOOT_TYPE_FILES.nomal);
}
const Q2_NONE = PILOT_COPY.engine_keys.q2_none;
const Q3_NONE = PILOT_COPY.engine_keys.q3_none;
const Q2_HALLUX = PILOT_COPY.engine_keys.q2_hallux;
const Q2_BALL = PILOT_COPY.engine_keys.q2_ball;
const Q2_INSTEP = PILOT_COPY.engine_keys.q2_instep;
const Q2_PINKY = PILOT_COPY.engine_keys.q2_pinky;
const Q2_INDEX = PILOT_COPY.engine_keys.q2_index;
const Q2_HOTSPOTS = [
  {id:"hallux", num:1, name:"엄지발가락(무지외반)", left:"59%", top:"39%"},
  {id:"index", num:2, name:"검지발가락", left:"50%", top:"30%", optKey:"index"},
  {id:"pinky", num:3, name:"새끼발가락", left:"41%", top:"36%", optKey:"pinky"},
  {id:"instep", num:4, name:"발등", left:"50%", top:"44%", optKey:"instep"}
];
function q2HotspotAriaLabel(h){
  return h.num + ". " + h.name;
}
function q2OptForHotspot(h){
  if(h.id==="hallux") return Q2_HALLUX;
  if(h.optKey==="index") return Q2_INDEX;
  if(h.optKey==="instep") return Q2_INSTEP;
  if(h.optKey==="pinky") return Q2_PINKY;
  return "";
}
function isQ2HotspotOn(h){
  const opt = q2OptForHotspot(h);
  return opt && answers.q2.includes(opt);
}
function toggleQ2Hotspot(h){
  const opt = q2OptForHotspot(h);
  if(opt) toggleQ2Option(opt);
}
function q2HotspotMarkerHtml(h){
  const on = isQ2HotspotOn(h);
  const aria = q2HotspotAriaLabel(h);
  return '<button type="button" class="q2-hotspot q2-hotspot-map'+(on?" on":"")+'" data-q2-zone="'+h.id+'" style="left:'+h.left+";top:"+h.top+'" aria-pressed="'+(on?"true":"false")+'" aria-label="'+escHtml(aria)+'">'
    +'<span class="q2-map-pin">'
    +'<span class="q2-dot" aria-hidden="true"></span>'
    +'<span class="q2-num-badge" aria-hidden="true">'+h.num+'</span>'
    +'</span></button>';
}
function q2LegendHtml(){
  let rows = "";
  Q2_HOTSPOTS.forEach(h=>{
    const on = isQ2HotspotOn(h);
    const aria = q2HotspotAriaLabel(h);
    rows += '<button type="button" class="q2-legend-item'+(on?" on":"")+'" data-q2-zone="'+h.id+'" aria-pressed="'+(on?"true":"false")+'" aria-label="'+escHtml(aria)+'">'
      +'<span class="q2-num-badge" aria-hidden="true">'+h.num+'</span>'
      +'<span class="q2-legend-label">'+escHtml(h.name)+'</span></button>';
  });
  const noneOn = answers.q2.includes(Q2_NONE);
  rows += '<button type="button" class="q2-legend-item q2-legend-none'+(noneOn?" on":"")+'" data-q2-none="1" aria-pressed="'+(noneOn?"true":"false")+'" aria-label="5. '+escHtml(Q2_NONE)+'">'
    +'<span class="q2-num-badge" aria-hidden="true">5</span>'
    +'<span class="q2-legend-label">'+escHtml(Q2_NONE)+'</span></button>';
  return '<div class="q2-legend">'+rows+'</div>';
}
function q2FootPhotoHtml(){
  const url = footImgUrl("nomal.jpg");
  let markers = "";
  Q2_HOTSPOTS.forEach(h=>{ markers += q2HotspotMarkerHtml(h); });
  return '<div class="q2-map-stack"><div class="q2-foot-stage"><img class="q2-foot-photo" src="'+url+'" alt="" width="600" height="706" decoding="async"/>'
    +'<div class="q2-hotspot-layer">'+markers+'</div></div>'
    +q2LegendHtml()+'</div>';
}
function toggleQ2Option(o){
  if(o===Q2_NONE){ answers.q2=[Q2_NONE]; return; }
  answers.q2 = answers.q2.filter(x=>x!==Q2_NONE);
  if(answers.q2.includes(o)) answers.q2 = answers.q2.filter(x=>x!==o);
  else answers.q2.push(o);
}
const Q2_TO_ZONE={};
Q2_TO_ZONE[Q2_HALLUX]="hallux";
Q2_TO_ZONE[Q2_BALL]="ball";
Q2_TO_ZONE[Q2_INDEX]="index_toe";
Q2_TO_ZONE[Q2_INSTEP]="instep";
Q2_TO_ZONE[Q2_PINKY]="pinky";
function q2StepChoicesHtml(){
  return '<div class="q2-step step-split">'
    +'<div class="q2-foot-panel">'
    +'<div class="q2-map-wrap" id="q2-map-root">'+q2FootPhotoHtml()+'</div>'
    +'<p class="map-caption">발 위 숫자 또는 아래 목록을 눌러 선택하세요.<br/>특정 부위는 여러 곳 가능 · 없으면 5번</p>'
    +'</div></div>';
}
function bindQ2Activate(btn, h){
  const activate = (ev)=>{
    if(ev.type==="keydown" && ev.key!=="Enter" && ev.key!==" ") return;
    if(ev.type==="keydown") ev.preventDefault();
    toggleQ2Hotspot(h);
    render();
  };
  btn.onclick = activate;
  btn.onkeydown = activate;
}
function bindQ2MapAndChips(el){
  const mapRoot = el.querySelector("#q2-map-root");
  if(mapRoot){
    mapRoot.querySelectorAll(".q2-hotspot[data-q2-zone], .q2-legend-item[data-q2-zone]").forEach(btn=>{
      const zoneId = btn.getAttribute("data-q2-zone");
      const h = Q2_HOTSPOTS.find(x=>x.id===zoneId);
      if(!h) return;
      bindQ2Activate(btn, h);
    });
  }
  el.querySelectorAll(".q2-legend-item[data-q2-none]").forEach(btn=>{
    const activate = (ev)=>{
      if(ev.type==="keydown" && ev.key!=="Enter" && ev.key!==" ") return;
      if(ev.type==="keydown") ev.preventDefault();
      toggleQ2Option(Q2_NONE);
      render();
    };
    btn.onclick = activate;
    btn.onkeydown = activate;
  });
}
function footImgUrl(file){ return FOOT_IMG_BASE+"/"+encodeURIComponent(footImgFileNormalized(file)); }
function painDotsFromQ2(q2){
  const list = Array.isArray(q2) ? q2 : [];
  if(!list.length || list.includes(Q2_NONE)) return [];
  const zones = [];
  if(list.includes(Q2_HALLUX)){ zones.push("hallux"); }
  if(list.includes(Q2_INDEX)){ zones.push("index_toe"); }
  if(list.includes(Q2_BALL)){ zones.push("ball"); }
  if(list.includes(Q2_INSTEP)){ zones.push("instep"); }
  if(list.includes(Q2_PINKY)){ zones.push("pinky"); }
  return zones;
}
function painMarkersHtml(zoneIds){
  if(!zoneIds || !zoneIds.length) return "";
  const base = {
    hallux:{left:20,bottom:22},
    index_toe:{left:32,bottom:26},
    ball:{left:50,top:48},
    instep:{left:50,top:18},
    pinky:{left:41, top:39}
  };
  const bunionDots = {
    hallux:{left:59,bottom:58},
    index_toe:{left:50,bottom:63}
  };
  const wideBallDots = {
    left:{left:38,bottom:53},
    right:{left:60,bottom:53}
  };
  const instepDot = {left:50,bottom:52};
  function dotStyle(pos){
    if(pos.right != null) return "right:"+pos.right+"%;bottom:"+pos.bottom+"%";
    if(pos.top != null) return "left:"+pos.left+"%;top:"+pos.top+"%";
    return "left:"+pos.left+"%;bottom:"+pos.bottom+"%";
  }
  function markersForZone(z){
    if(z==="hallux" || z==="index_toe") return [bunionDots[z]];
    if(z==="ball") return [wideBallDots.left, wideBallDots.right];
    if(z==="instep") return [instepDot];
    const p = base[z];
    return p ? [p] : [];
  }
  let h = "";
  zoneIds.forEach(z=>{
    markersForZone(z).forEach(pos=>{
      h += '<span class="pain-dot" style="'+dotStyle(pos)+'"></span>';
    });
  });
  return h;
}
function specLinesHtml(lines){
  if(!lines || !lines.length){
    return '<p class="foot-spec-line" style="color:var(--muted)">—</p>';
  }
  return lines.map(l=>'<p class="foot-spec-line">'+escHtml(l)+'</p>').join("");
}
function footSpecReferenceLines(){
  const lines = PILOT_COPY.foot_compare && PILOT_COPY.foot_compare.reference_spec;
  return (lines && lines.length) ? lines.slice() : ["발유형: 보통발","발볼: 보통","발등: 보통","발길이: 정사이즈"];
}
function footTypeSpecLabel(typeKey, pCode){
  if(String(pCode||"").toUpperCase()==="P1") return "무지외반";
  const m = {nomal:"보통발",wide:"넓은발",narrow:"좁은발",bunion:"무지외반",slender:"좁은발"};
  return m[typeKey]||"보통발";
}
function footTypeSpecValue(data){
  const fp = data.foot_profile || {};
  const typeKey = footCustomerTypeKey(data);
  const p = String(fp.p_code||"P0").toUpperCase();
  const r = String(fp.r_code||"R1").toUpperCase();
  const q2 = activeQ2List(data.q2 || (data.foot_compare && data.foot_compare.q2) || []);
  const hasBallQ2 = q2.includes(Q2_BALL);
  if((p==="P1" || q2.includes(Q2_HALLUX)) && !hasBallQ2) return "무지외반";
  const hasHallux = p==="P1" || q2.includes(Q2_HALLUX) || q2.includes(Q2_INDEX);
  const isWide = r==="R2"||r==="R5" || typeKey==="wide";
  const parts = [];
  if(isWide) parts.push("넓은발");
  if(hasHallux) parts.push("무지외반");
  if(parts.length) return parts.join(" / ");
  return footTypeSpecLabel(typeKey, fp.p_code);
}
function footBallSpecLabel(rCode, sCode, data){
  const fp = (data && data.foot_profile) || {};
  const p = String(fp.p_code||"P0").toUpperCase();
  const q2 = data ? activeQ2List(data.q2 || (data.foot_compare && data.foot_compare.q2) || []) : [];
  const hasBallQ2 = q2.includes(Q2_BALL);
  const hasHallux = p==="P1" || q2.includes(Q2_HALLUX);
  const r = String(rCode||"R1").toUpperCase();
  const s = String(sCode||"S0").toUpperCase();
  if(r==="R2"||r==="R5" || hasBallQ2){
    if(s==="S3") return "아주넓음";
    return "넓음";
  }
  if(hasHallux && !hasBallQ2){
    if(s==="S3") return "아주넓음";
    if(s==="S1"||s==="S2") return "넓음";
    return "보통";
  }
  return "보통";
}
function footInstepSpecLabel(rCode, sCode, data){
  const fp = (data && data.foot_profile) || {};
  const p = String(fp.p_code||"P0").toUpperCase();
  const q2 = data ? activeQ2List(data.q2 || (data.foot_compare && data.foot_compare.q2) || []) : [];
  const hasInstep = p==="P3" || q2.includes(Q2_INSTEP);
  const r = String(rCode||"R1").toUpperCase();
  const s = String(sCode||"S0").toUpperCase();
  if(hasInstep){
    if(s==="S3") return "매우 높음";
    if(s==="S1"||s==="S2") return "높은편";
    return "보통";
  }
  return (r==="R4"||r==="R5")?"높음":"보통";
}
function footLengthSpecLabel(data){
  const q1 = (data && data.q1) || "";
  const code = String((data && data.recommendation_code) || "").toUpperCase();
  const fc = PILOT_COPY.foot_compare || {};
  if(q1===Q1_SLIP) return fc.length_slip || "정사이즈 보다 작음";
  if(code==="SF04") return fc.length_sf04 || "정사이즈 또는 약간 긴발";
  return "정사이즈";
}
function footCustomerSpecLines(data){
  const fp = data.foot_profile || {};
  return [
    "발유형: "+footTypeSpecValue(data),
    "발볼: "+footBallSpecLabel(fp.r_code, fp.s_code, data),
    "발등: "+footInstepSpecLabel(fp.r_code, fp.s_code, data),
    "발길이: "+footLengthSpecLabel(data)
  ];
}
function footCompareHtml(data){
  const fc = data.foot_compare;
  if(!fc || !fc.reference || !fc.customer) return "";
  const q2list = data.q2 || fc.q2 || [];
  function tier(p, label, mod, specLines){
    const imgFile = mod==="cust" ? footCustomerImageFile(data) : footImgFileNormalized(p.image);
    const url = footImgUrl(imgFile);
    const imgLabel = mod==="cust" ? footTypeSpecValue(data) : (p.label||"");
    const specs = '<p class="foot-compare-spec-title">'+escHtml(label)+'</p>'+specLinesHtml(specLines);
    let pain = "";
    if(mod==="cust"){
      const zones = painDotsFromQ2(q2list);
      if(zones.length) pain = painMarkersHtml(zones);
      else if(p.pain_zones && p.pain_zones.length) pain = painMarkersHtml(p.pain_zones);
    }
    return '<div class="foot-compare-tier foot-compare-tier--'+mod+'">'
      +'<div class="foot-compare-row">'
      +'<div class="foot-compare-img-cell"><div class="foot-compare-img-stage"><img src="'+url+'" alt="'+escHtml(imgLabel)+'" loading="lazy"/>'+pain+'</div></div>'
      +'<div class="foot-compare-spec-list">'+specs+'</div>'
      +'</div></div>';
  }
  const fcCopy = PILOT_COPY.foot_compare || {};
  const blockTitle = fcCopy.block_title || "내 발유형 비교하기";
  return '<div class="foot-compare-block"><div class="foot-compare-card">'
    +'<div class="foot-compare-head"><h3 class="foot-compare-block-title result-sec-title">'+escHtml(blockTitle)+'</h3></div>'
    +'<div class="foot-compare-body"><div class="foot-compare-stack">'
    +tier(fc.reference, fcCopy.reference_title, "ref", footSpecReferenceLines())
    +tier(fc.customer, fcCopy.customer_title, "cust", footCustomerSpecLines(data))
    +'</div></div></div>'
    +'<p class="foot-compare-note">'+escHtml(fcCopy.pain_note)+'</p></div>';
}
function finishIntro(){
  if(introTimer){ clearInterval(introTimer); introTimer = null; }
  introActive = false;
  const k = "sf_pilot_intro_done:"+(src||"web")+":"+(productId||"_");
  try { sessionStorage.setItem(k, "1"); } catch(_) {}
  step = 0;
  render();
}
function renderIntro(){
  hideBottomBar();
  const el = document.getElementById("step");
  el.classList.add("intro-step");
  el.classList.remove("pilot-q2-step");
  el.classList.remove("hidden");
  document.getElementById("result").classList.add("hidden");
  const t = FOOT_INTRO_TYPES[introIndex];
  el.innerHTML = '<div class="intro-hero">'
    +'<div class="intro-head"><p class="intro-brand">Every Fit</p>'
    +'<h1>'+escHtml(PILOT_COPY.intro.title)+'</h1></div>'
    +'<div class="intro-visual"><div class="intro-img-frame"><div class="intro-foot-stage"><img class="intro-foot-img" id="intro-img" src="'+footImgUrl(t.file)+'" alt="" width="272" height="238" decoding="async"/>'
    +'<p class="intro-tagline">'+escHtml(PILOT_COPY.intro.tagline)+'</p></div></div></div>'
    +'<div class="cta-wrap"><button type="button" class="btn primary" id="intro-start">'+escHtml(PILOT_COPY.intro.start_button)+'</button></div>'
    +'<p class="intro-build" aria-hidden="true">'+escHtml(PILOT_BUILD)+'</p></div>';
  document.body.classList.add("intro-screen");
  document.getElementById("intro-start").onclick = finishIntro;
  if(introTimer) clearInterval(introTimer);
  const reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if(!reduceMotion){
    introTimer = setInterval(()=>{
      introIndex = (introIndex+1) % FOOT_INTRO_TYPES.length;
      const tt = FOOT_INTRO_TYPES[introIndex];
      const img = document.getElementById("intro-img");
      if(img){ img.src = footImgUrl(tt.file); }
    }, 500);
  }
}
function bootPilot(){
  const k = "sf_pilot_intro_done:"+(src||"web")+":"+(productId||"_");
  if((params.get("nointro")||"")==="1") introActive = false;
  else if((params.get("forceintro")||"")==="1") introActive = true;
  else {
    try { introActive = !sessionStorage.getItem(k); } catch(_) { introActive = true; }
  }
  if(introActive) renderIntro();
  else render();
}
function progressPct(){ return Math.round(((step+1)/4)*100); }
function progressBarHtml(){
  return '<div class="progress-bar" aria-hidden="true"><i style="width:'+progressPct()+'%"></i></div>'
    +'<p class="step-progress">'+(step+1)+' / 4</p>';
}
function footSvgHtml(large, interactive){
  const cls = "foot-map"+(large?" foot-map-lg":"")+(interactive?" q2-interactive":"");
  return '<svg class="'+cls+'" viewBox="0 0 120 220" role="img" aria-label="발 편안 지도">'
    +'<path class="sole" d="M60 12 C42 12 30 28 28 48 L22 120 C18 155 22 188 38 208 C48 218 72 218 82 208 C98 188 102 155 98 120 L92 48 C90 28 78 12 60 12 Z"/>'
    +'<ellipse class="zone" data-zone="hallux" cx="38" cy="175" rx="16" ry="22"/>'
    +'<ellipse class="zone" data-zone="ball" cx="60" cy="130" rx="28" ry="24"/>'
    +'<ellipse class="zone" data-zone="instep" cx="60" cy="72" rx="22" ry="28"/>'
    +'<ellipse class="zone" data-zone="pinky" cx="82" cy="178" rx="12" ry="18"/>'
    +'</svg>';
}
function q3Level(){
  if(answers.q3===Q3_NONE) return 0;
  if(answers.q3==="매우 불편해요") return 4;
  if(answers.q3==="자주 불편해요") return 3;
  return 2;
}
function zonesFromAnswers(){
  if(step<1) return [];
  if(step===1){
    if(!answers.q2.length || answers.q2.includes(Q2_NONE)) return [];
    return answers.q2.map(o=>Q2_TO_ZONE[o]).filter(Boolean);
  }
  const z = [];
  (answers.q2||[]).forEach(o=>{ const zid=Q2_TO_ZONE[o]; if(zid) z.push(zid); });
  return z;
}
function applyMapPreview(root){
  if(!root) return;
  const zones = zonesFromAnswers();
  const lv = step>=3 ? q3Level() : (step>=2 ? Math.max(q3Level(),2) : 2);
  root.querySelectorAll(".zone").forEach(el=>{
    el.classList.remove("on","lv2","lv3","lv4","comfort");
    const z = el.getAttribute("data-zone");
    if(zones.includes(z)){
      el.classList.add("on");
      if(lv>=4) el.classList.add("lv4");
      else if(lv>=3) el.classList.add("lv3");
      else el.classList.add("lv2");
    }
  });
}
function applyMapFromProfile(root, fp){
  if(!root || !fp) return;
  const p = (fp.p_code||"P0").toUpperCase();
  const s = (fp.s_code||"S0").toUpperCase();
  const pmap = {P1:["hallux"],P2:["ball"],P3:["instep"],P4:["pinky"],P5:["hallux","ball","instep","pinky"]};
  let zones = pmap[p]||[];
  if(p==="P0") zones=[];
  let lv = 2;
  if(s==="S3") lv=4; else if(s==="S2") lv=3;
  root.querySelectorAll(".zone").forEach(el=>{
    el.classList.remove("on","lv2","lv3","lv4","comfort");
    const z = el.getAttribute("data-zone");
    if(p==="P0"){ el.classList.add("comfort"); return; }
    if(zones.includes(z)){
      el.classList.add("on");
      if(lv>=4) el.classList.add("lv4");
      else if(lv>=3) el.classList.add("lv3");
      else el.classList.add("lv2");
    }
  });
}
function comfortBarsHtml(ux){
  const bars = ux && ux.comfort_bars;
  if(!bars) return "";
  function row(item){
    const n = Math.max(1, Math.min(5, parseInt(item.level,10)||1));
    let dots = "";
    for(let i=1;i<=5;i++) dots += '<i class="'+(i<=n?"on":"")+'"></i>';
    return '<div class="comfort-row"><span class="lbl">'+item.label+'</span><div class="comfort-dots">'+dots+'</div></div>';
  }
  return '<div class="comfort-bars"><h3>예상 편안함 (참고)</h3>'
    +row(bars.order_as_is)+row(bars.with_guidance)
    +(bars.hint?'<p class="comfort-hint">'+bars.hint+'</p>':"")
    +'</div>';
}
function escHtml(s){ return (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
function tipTextHtml(s){ return escHtml(s).split(String.fromCharCode(10)).join("<br>"); }
const STRETCH_TIP_PRECISION_NOTE = PILOT_COPY.result.stretch_prec_note;
function tipLineSummary(text, maxLen){
  maxLen = maxLen || 44;
  const lines = (text||"").split(String.fromCharCode(10)).map(s=>s.trim()).filter(Boolean);
  const flat = (lines[0]||"").replace(/\\s+/g," ").trim();
  const empty = (PILOT_COPY.result && PILOT_COPY.result.tip_row_empty_summary) || "자세히 보기";
  if(!flat) return empty;
  if(flat.length <= maxLen) return flat;
  return flat.slice(0, maxLen - 1) + "…";
}
function showNaverExchangeTipRow(data){
  if(!naverChannel) return false;
  const fr = data.fit_result || {};
  if(fr.exchange_event_active === false) return false;
  const code = (data.recommendation_code||"").toUpperCase();
  if(code==="SF00") return false;
  return !!naverDiagnosisCopyText(data);
}
function tipGuideRowHtml(kind, title, summary){
  return '<button type="button" class="tip-guide-row" data-tip-sheet="'+escHtml(kind)+'" aria-haspopup="dialog">'
    +'<span class="tip-row-title">'+escHtml(title)+'</span>'
    +'<span class="tip-row-summary">'+escHtml(summary)+'</span>'
    +'<span class="tip-row-chevron" aria-hidden="true">›</span></button>';
}
function tipGuideBlockHtml(data){
  const fr = data.fit_result || {};
  const fitTip = fr.fit_recommendation_tip;
  const stretchTip = fr.stretch_recommendation_tip;
  const resCopy = PILOT_COPY.result || {};
  let rows = "";
  if(fitTip){
    rows += tipGuideRowHtml("fit", resCopy.tip_fit_title, tipLineSummary(fitTip));
  }else if(!naverChannel && fr.order_tip){
    rows += tipGuideRowHtml("fit", resCopy.tip_fit_title || "주문 안내", tipLineSummary(fr.order_tip));
  }
  if(naverChannel || stretchTip || STRETCH_TIP_PRECISION_NOTE){
    const stretchSum = stretchTip ? tipLineSummary(stretchTip) : tipLineSummary(STRETCH_TIP_PRECISION_NOTE);
    rows += tipGuideRowHtml("stretch", resCopy.tip_stretch_title, stretchSum);
  }
  if(!rows){
    if(fr.alt_tip){
      return '<p class="sub" style="margin:8px 0">'+escHtml(fr.alt_tip)+'</p>';
    }
    return "";
  }
  return '<div class="tip-guide-block tip-guide-block--nohead">'+rows+'</div>';
}
function openFitTipSheet(){
  if(!resultPayload) return;
  const data = resultPayload;
  const fr = data.fit_result || {};
  const body = fr.fit_recommendation_tip || fr.order_tip || "";
  postPilotFunnelEvent("tip_sheet_fit", diagnosisId);
  openPilotSheet('<h2>'+escHtml(PILOT_COPY.result.tip_fit_title)+'</h2>'
    +'<div class="sheet-body-tip">'+tipTextHtml(body)+'</div>'
    +'<button type="button" class="sheet-close" id="sheet-close">닫기</button>');
}
function openStretchTipSheet(){
  if(!resultPayload) return;
  const data = resultPayload;
  const fr = data.fit_result || {};
  const main = fr.stretch_recommendation_tip || "";
  postPilotFunnelEvent("tip_sheet_stretch", diagnosisId);
  let body = '<div class="sheet-body-tip">';
  if(main) body += tipTextHtml(main)+'<br><br>';
  body += '<span class="stretch-prec-note">'+escHtml(STRETCH_TIP_PRECISION_NOTE)+'</span></div>';
  if(fr.alt_tip){
    body += '<p class="sub" style="margin:0 0 12px">'+escHtml(fr.alt_tip)+'</p>';
  }
  openPilotSheet('<h2>'+escHtml(PILOT_COPY.result.tip_stretch_title)+'</h2>'+body
    +'<button type="button" class="sheet-close" id="sheet-close">닫기</button>');
}
function bindTipGuideRows(){
  document.querySelectorAll(".tip-guide-row").forEach(btn=>{
    btn.onclick = ()=>{
      const k = btn.getAttribute("data-tip-sheet");
      if(k==="fit") openFitTipSheet();
      else if(k==="stretch") openStretchTipSheet();
    };
  });
}
function naverExchangeBlockHtml(data){
  if(!showNaverExchangeTipRow(data)) return "";
  const resCopy = PILOT_COPY.result || {};
  const body = resCopy.exchange_sheet_body
    || "진단 결과 복사하기를 누른 후 네이버 톡톡 창에 붙여넣기 해주시면, 1회 사이즈 교환 및 2차 사이즈 보정 서비스를 받으실 수 있어요.";
  const talkBtn = naverTalkUrl(data)
    ? '<button type="button" class="btn secondary" id="open-naver-talk" disabled>톡톡 열기</button>'
    : "";
  return '<div class="exchange-block">'
    +'<div class="exchange-card">'
    +'<div class="exchange-head"><h3 class="tip-box-title result-sec-title">'+escHtml(resCopy.tip_exchange_title)+'</h3></div>'
    +'<div class="exchange-body-bg">'
    +'<p>'+escHtml(body)+'</p>'
    +'<p class="sub">'+escHtml(resCopy.exchange_match_hint || "복사한 내용에 진단번호가 포함되어 있어요. 톡톡에 붙여넣어 주시면 주문·진단을 연결해 드립니다.")+'</p>'
    +'</div>'
    +'<div class="exchange-actions">'
    +'<button type="button" class="btn primary" id="copy-naver-ex">진단 결과 복사하기</button>'
    +talkBtn
    +'</div></div></div>';
}
function fitDotsHtml(level){
  const n = Math.max(1, Math.min(5, parseInt(level,10)||1));
  let dots = "";
  for(let i=1;i<=5;i++) dots += '<i class="'+(i<=n?"on":"")+'"></i>';
  return '<div class="comfort-dots">'+dots+'</div>';
}
function naverDiagnosisCopyText(data){
  return data.naver_diagnosis_copy || data.inquiry_copy_naver_exchange || "";
}
function naverTalkUrl(data){
  return (data.store_links && data.store_links.talktalk_url) || "";
}
async function copyNaverDiagnosisToClipboard(data){
  const text = naverDiagnosisCopyText(data);
  if(!text) return false;
  await navigator.clipboard.writeText(text);
  postPilotFunnelEvent("pilot_copy_naver_exchange", diagnosisId);
  return true;
}
function openNaverTalktalkWindow(data){
  const talkUrl = naverTalkUrl(data);
  if(!talkUrl) return;
  postPilotFunnelEvent("talktalk_open", diagnosisId);
  window.open(talkUrl, "_blank", "noopener");
}
function bindCopyThenTalkButtons(data, copyId, talkId, copyLabel){
  copyLabel = copyLabel || "진단 결과 복사하기";
  const copyBtn = document.getElementById(copyId);
  const talkBtn = talkId ? document.getElementById(talkId) : null;
  const talkUrl = naverTalkUrl(data);
  if(talkBtn){
    talkBtn.disabled = true;
    if(!talkUrl) talkBtn.style.display = "none";
    else talkBtn.onclick = ()=> openNaverTalktalkWindow(data);
  }
  if(!copyBtn) return;
  copyBtn.onclick = async ()=>{
    const ok = await copyNaverDiagnosisToClipboard(data);
    if(!ok){ alert("복사할 진단 결과가 없습니다."); return; }
    const prev = copyBtn.textContent;
    copyBtn.textContent = "복사했어요!";
    if(talkBtn && talkUrl) talkBtn.disabled = false;
    setTimeout(()=>{ copyBtn.textContent = prev || copyLabel; }, 2200);
  };
}
function fitResultHtml(data){
  const fr = data.fit_result;
  if(!fr || !fr.fit_lines) return comfortBarsHtml(data.ux_scores||{});
  const rec = fr.recommended_fit_line || "";
  let rows = "";
  fr.fit_lines.forEach(row=>{
    const cls = row.fit_line===rec ? "fit-line-row rec" : "fit-line-row";
    rows += '<div class="'+cls+'"><span class="fit-name">'+escHtml(row.fit_line)
      +(row.fit_line===rec?" ★":"")+'</span>'+fitDotsHtml(row.comfort_level)
      +'<span style="flex:0 0 36px;text-align:right;font-size:12px;color:#64748b">'+escHtml(row.comfort_label)+'</span></div>';
  });
  let narr = "";
  (fr.narrative_lines||[]).forEach(l=>{ narr += '<p>'+escHtml(l.trim())+'</p>'; });
  const narrTitle = (PILOT_COPY.result && PILOT_COPY.result.narrative_block_title) || "고객님 발 특성 (참고)";
  const narrBlock = narr
    ? '<div class="foot-type-block"><h3 class="result-sec-title">'+escHtml(narrTitle)+'</h3>'+narr+'</div>'
    : "";
  return narrBlock
    +'<div class="fit-lines-block" id="fit-lines-anchor"><h3 class="result-sec-title">'+escHtml(PILOT_COPY.result.fit_block_title)+'</h3>'+rows+'</div>'
    +tipGuideBlockHtml(data)
    +naverExchangeBlockHtml(data);
}
let resultPayload = null;
function hideBottomBar(){
  document.body.classList.remove("has-bottom-bar");
  const bar = document.getElementById("pilot-bottom-bar");
  if(bar) bar.classList.add("hidden");
}
function showBottomBar(data){
  if(!naverChannel) return;
  const links = data.store_links || {};
  const fr = data.fit_result || {};
  const bar = document.getElementById("pilot-bottom-bar");
  if(!bar) return;
  const talkBtn = document.getElementById("tab-talk");
  const fitBtn = document.getElementById("tab-fit");
  const precBtn = document.getElementById("tab-prec");
  const hasTalk = !!(links.has_talktalk || data.naver_diagnosis_copy
    || data.inquiry_copy_short || data.inquiry_copy_naver_exchange);
  if(talkBtn) talkBtn.disabled = !hasTalk;
  if(fitBtn) fitBtn.disabled = !links.has_fit_categories;
  if(precBtn) precBtn.disabled = !fr.precision_tab_eligible;
  bar.classList.remove("hidden");
  document.body.classList.add("has-bottom-bar");
}
function closePilotSheet(){
  const bd = document.getElementById("pilot-sheet-backdrop");
  if(bd) bd.classList.add("hidden");
}
function openPilotSheet(innerHtml){
  const sh = document.getElementById("pilot-sheet");
  const bd = document.getElementById("pilot-sheet-backdrop");
  if(!sh || !bd) return;
  sh.innerHTML = innerHtml;
  bd.classList.remove("hidden");
  const closeBtn = document.getElementById("sheet-close");
  if(closeBtn) closeBtn.onclick = closePilotSheet;
  bd.onclick = (e)=>{ if(e.target===bd) closePilotSheet(); };
}
function talkCopyPrimary(data){
  if(naverChannel && data.naver_diagnosis_copy) return data.naver_diagnosis_copy;
  const fr = data.fit_result || {};
  if(data.inquiry_copy_naver_exchange && fr.exchange_event_active !== false) return data.inquiry_copy_naver_exchange;
  if(data.inquiry_copy_short) return data.inquiry_copy_short;
  return data.inquiry_copy_text || "";
}
function openTalkSheet(){
  if(!resultPayload) return;
  postPilotFunnelEvent("talk_guide_open", diagnosisId);
  const data = resultPayload;
  const preview = talkCopyPrimary(data);
  const useDxCopy = !!(naverChannel && data.naver_diagnosis_copy);
  const hints = useDxCopy
    ? [
        "① 아래 [진단 결과 복사하기]를 눌러 주세요.",
        "② [톡톡 열기] 후 붙여넣어 보내 주세요. (네이버 로그인 필요할 수 있어요)",
        "③ 붙여넣으시면 1회 사이즈 교환·2차 보정 안내를 받으실 수 있어요.",
      ]
    : ((data.fit_result && data.fit_result.talk_sheet_hints) || []);
  let hintHtml = '<ol class="sheet-hints">';
  hints.forEach(h=>{ hintHtml += "<li>"+escHtml(h)+"</li>"; });
  hintHtml += "</ol>";
  const talkUrl = naverTalkUrl(data);
  const loginNote = talkUrl
    ? '<p class="sub" style="margin:0 0 10px"><b>진단 결과 복사</b> 후 <b>톡톡 열기</b>로 붙여넣어 주세요. 네이버 <b>로그인</b>이 필요할 수 있습니다.</p>'
    : '<p class="sub" style="margin:0 0 10px">복사한 문구를 <b>네이버 쇼핑 앱</b> → 톡톡·문의에 붙여넣어 주세요.</p>';
  const copyLabel = useDxCopy ? "진단 결과 복사하기" : "한 줄 복사";
  openPilotSheet('<h2>톡톡 문의</h2>'
    +loginNote
    +'<div class="sheet-preview">'+escHtml(preview)+'</div>'
    +hintHtml
    +'<div class="sheet-actions">'
    +'<button type="button" class="btn-sheet primary" id="sheet-copy-talk">'+escHtml(copyLabel)+'</button>'
    +(talkUrl ? '<button type="button" class="btn-sheet secondary" id="sheet-open-talk" disabled>톡톡 열기</button>' : '')
    +'</div><button type="button" class="sheet-close" id="sheet-close">닫기</button>');
  if(useDxCopy){
    bindCopyThenTalkButtons(data, "sheet-copy-talk", talkUrl ? "sheet-open-talk" : null, copyLabel);
  }else{
    const cp = document.getElementById("sheet-copy-talk");
    const op = document.getElementById("sheet-open-talk");
    if(op && talkUrl){
      op.disabled = true;
      op.onclick = ()=> openNaverTalktalkWindow(data);
    }
    if(cp){
      cp.onclick = async ()=>{
        await navigator.clipboard.writeText(preview);
        postPilotFunnelEvent("pilot_copy_inquiry_short", diagnosisId);
        cp.textContent = "복사했어요!";
        if(op && talkUrl) op.disabled = false;
        setTimeout(()=>{ cp.textContent = copyLabel; }, 2200);
      };
    }
  }
}
function openFitSheet(){
  if(!resultPayload) return;
  const data = resultPayload;
  const links = data.store_links || {};
  const cats = links.fit_category_urls || {};
  const rec = (data.fit_result && data.fit_result.recommended_fit_line) || "";
  let btns = "";
  ["기본핏","편한핏","아주 편한핏"].forEach(name=>{
    const url = cats[name];
    if(!url) return;
    const cls = name===rec ? "fit-cat-btn rec" : "fit-cat-btn";
    btns += '<button type="button" class="'+cls+'" data-url="'+escHtml(url)+'" data-fit="'+escHtml(name)+'">'+escHtml(name)+' 상품 보기</button>';
  });
  openPilotSheet('<h2>핏별 상품</h2>'
    +'<p class="sub" style="margin:0 0 12px">스토어에서 '+escHtml(rec)+'에 맞는 상품을 모아 두었어요.</p>'
    +btns
    +'<button type="button" class="sheet-close" id="sheet-close">닫기</button>');
  document.querySelectorAll(".fit-cat-btn").forEach(btn=>{
    btn.onclick = ()=>{
      const url = btn.getAttribute("data-url");
      const fit = btn.getAttribute("data-fit")||"";
      postPilotFunnelEvent("fit_category_open", diagnosisId);
      if(url) window.open(url, "_blank", "noopener");
    };
  });
}
function bindBottomBar(data){
  showBottomBar(data);
  const talkBtn = document.getElementById("tab-talk");
  const fitBtn = document.getElementById("tab-fit");
  const precBtn = document.getElementById("tab-prec");
  if(talkBtn) talkBtn.onclick = ()=>{ if(!talkBtn.disabled) openTalkSheet(); };
  if(fitBtn) fitBtn.onclick = ()=>{ if(!fitBtn.disabled) openFitSheet(); };
  if(precBtn) precBtn.onclick = ()=>{
    if(precBtn.disabled){
      alert(PILOT_COPY.alerts.prec_tab_blocked);
      return;
    }
    showPrecisionBlocks(false);
    closePilotSheet();
  };
}
function finishQ1NoDiscomfort(){
  answers.q1 = Q1_NONE;
  answers.q2 = [Q2_NONE];
  answers.q3 = Q3_NONE;
  submit();
}
const steps = PILOT_COPY.steps;
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
  const followupMsg = naverChannel
    ? '<p>보내주신 발 모양 사진과 정밀 진단 정보를 분석한 뒤, 간편 진단 결과를 반영해 <b>네이버 톡톡</b>으로 발볼·사이즈 안내를 드립니다.</p>'
    : '<p>보내주신 발 모양 사진과 입력해 주신 정밀 진단 정보를 함께 분석한 후, 간편 진단 결과를 반영하여 보다 정확한 발볼 늘림 안내 정보를 카카오톡으로 안내해 드립니다.</p>';
  return '<div class="prec-done">'
    +'<p class="prec-done-title">정밀 진단 접수가 완료되었습니다. 👣</p>'
    +photoNote
    +followupMsg
    +'<p>진단 결과는 보통 1~2시간 내 확인하실 수 있으며, 순차적으로 안내드리고 있습니다.</p>'
    +'<p>감사합니다. 😊</p>'
    +(href
      ? '<a class="btn-detail-back" href="'+href+'" rel="noopener">'+orderBackLabel()+'</a>'
      : (naverChannel
        ? '<p class="result-back-hint">네이버 쇼핑 앱으로 돌아가 주문해 주세요.</p>'
        : '<p class="result-back-hint">쿠팡 앱으로 돌아가 주문해 주세요.</p>'))
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
    if(safeSessionGet(key)==="1") return;
    safeSessionSet(key,"1");
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
const PILOT_BUILD = "__PILOT_BUILD__";
function render(){
  hideBottomBar();
  const el = document.getElementById("step");
  el.classList.remove("intro-step", "pilot-q2-step");
  document.body.classList.remove("intro-screen");
  if(step >= steps.length){ if(!submitInFlight) submit(); return; }
  const s = steps[step];
  if(s.key==="q2") el.classList.add("pilot-q2-step");
  let html = '<p class="pilot-step-brand">Every Fit</p>'+progressBarHtml()+'<h1>'+s.title+"</h1>";
  if(s.hint){ html += '<p class="sub">'+s.hint+'</p>'; }
  let choices = "";
  if(s.size){
    choices = '<div class="chips-size-grid">'+sizes.map(v=>'<button type="button" class="chip'+(answers.q4===v?" on":"")+'" data-size="'+v+'">'+v+'</button>').join("")+'</div>';
  } else if(s.multi && s.key==="q2"){
    choices = q2StepChoicesHtml();
  } else if(s.multi){
    choices = '<div class="step-choices chips-col">'+s.opts.map(o=>'<span class="chip'+(answers.q2.includes(o)?" on":"")+'" data-o="'+o+'">'+o+'</span>').join("")+'</div>';
  } else {
    choices = '<div class="step-choices">';
    s.opts.forEach(o=>{ choices += '<button type="button" class="btn'+(answers[s.key]===o?" on":"")+'" data-o="'+o+'">'+o+'</button>'; });
    choices += '</div>';
  }
  html += choices+'<div class="cta-wrap"><button type="button" class="btn primary" id="next">'+(s.nextBtn||PILOT_COPY.common.next_default)+'</button>';
  if(step > 0){ html += '<button type="button" class="btn-step-back" id="step-back">'+escHtml(PILOT_COPY.common.step_back)+'</button>'; }
  html += '</div>';
  if(step===0 && !naverChannel){ html += '<p class="build-tag">빌드 '+PILOT_BUILD+'</p>'; }
  el.innerHTML = html;
  if(s.key==="q2" && s.multi){ bindQ2MapAndChips(el); }
  if(s.size){
    el.querySelectorAll(".chips-size-grid [data-size]").forEach(b=>{
      b.onclick = (ev)=>{
        ev.preventDefault();
        const v = parseInt(b.getAttribute("data-size"), 10);
        if(!isNaN(v)){ answers.q4 = v; render(); }
      };
    });
  }
  if(!(s.key==="q2" && s.multi)){
    el.querySelectorAll(".btn[data-o], .chip[data-o]").forEach(b=>{
      b.onclick = ()=>{
        const o = b.dataset.o;
        if(s.size) return;
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
  }
  document.getElementById("next").onclick = ()=>{
    if(s.multi && !answers.q2.length){ alert(PILOT_COPY.common.q2_select_required); return; }
    if(!s.multi && !s.size && !answers[s.key]){ alert(PILOT_COPY.common.select_required); return; }
    step++; render();
  };
  const backBtn = document.getElementById("step-back");
  if(backBtn){
    backBtn.onclick = ()=>{ if(step > 0){ step--; render(); } };
  }
}
function pilotDiagnoseErrorMessage(data, res){
  if(data && data.error) return data.error;
  if(data && data.detail){
    if(typeof data.detail === "string") return data.detail;
    return "입력값을 확인해 주세요.";
  }
  if(res && !res.ok) return "진단 요청에 실패했습니다. (HTTP "+res.status+")";
  return "진단 결과를 받지 못했습니다. 잠시 후 다시 시도해 주세요.";
}
async function submit(){
  if(submitInFlight) return;
  submitInFlight = true;
  const stepEl = document.getElementById("step");
  try{
  stepEl.classList.remove("hidden");
  stepEl.innerHTML = '<p class="sub" style="text-align:center;padding:28px 12px;margin:0">'+escHtml(PILOT_COPY.result.submit_loading)+'</p>';
  let data;
  let res;
  try{
    res = await fetch("/pilot/diagnose",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({...answers, product_id:productId, channel:src})});
    data = await res.json();
  }catch(e){
    alert(PILOT_COPY.alerts.network_error);
    step = Math.min(step, steps.length - 1);
    render();
    return;
  }
  if(data.error || !res.ok || !data.diagnosis_code){
    alert(pilotDiagnoseErrorMessage(data, res));
    step = Math.min(step, steps.length - 1);
    render();
    return;
  }
  stepEl.classList.add("hidden");
  resultPayload = data;
  diagnosisId = data.id;
  postPilotFunnelEvent("pilot_result_view", diagnosisId);
  const r = document.getElementById("result");
  r.classList.remove("hidden");
  const code = data.recommendation_code;
  const sf00 = code==="SF00";
  const copyText = data.inquiry_copy_text || (data.message+"\\n\\n진단번호: "+data.diagnosis_code);
  const copyShort = data.inquiry_copy_short || "";
  const fr = data.fit_result || {};
  let primaryCta = "";
  if(!naverChannel){
    const market = coupangChannel;
    const stretch = code==="SF01" || code==="SF02";
    const copyLabel = stretch ? "발볼 늘림 안내문 복사하기" : "안내문 복사하기";
    if(!sf00){
      if(market && copyShort){
        primaryCta = '<div class="cta-wrap result-cta">'
          +'<button class="btn primary btn-inquiry-short" id="copy-short">한 줄로 문의 복사하기</button>'
          +'<button class="btn primary btn-inquiry-long" id="copy" style="margin-top:10px">자세한 안내 전체 복사</button></div>';
      }else{
        primaryCta = '<div class="cta-wrap result-cta"><button class="btn primary" id="copy">'+copyLabel+'</button></div>';
      }
    }
  }
  const precOptional = (!naverChannel && !sf00)
    ? '<div class="result-next-wrap" id="prec-optional-wrap">'
      +'<p class="result-next-hint">'+escHtml(PILOT_COPY.result.prec_optional_hint)+'</p>'
      +'<button type="button" class="btn-result-next" id="prec-optional">'+escHtml(PILOT_COPY.result.prec_optional_button)+'</button></div>'
    : "";
  const fp = data.foot_profile || {};
  const dxClass = naverChannel ? "result-dx naver-hide" : "result-dx";
  const compareBlock = footCompareHtml(data);
  r.innerHTML = compareBlock
    +resultMessageHtml(data)
    +fitResultHtml(data)
    +'<p class="'+dxClass+'"><b>진단번호: '+data.diagnosis_code+'</b></p>'
    +primaryCta
    +precOptional
    +resultDetailBackHtml(data.recommendation_code);
  document.getElementById("prec-teaser").classList.add("hidden");
  document.getElementById("precision").classList.add("hidden");
  bindBottomBar(data);
  bindTipGuideRows();
  bindCopyThenTalkButtons(data, "copy-naver-ex", "open-naver-talk");
  if(document.getElementById("copy-short")){
    document.getElementById("copy-short").onclick = async ()=>{
      await navigator.clipboard.writeText(copyShort);
      postPilotFunnelEvent("pilot_copy_inquiry_short", diagnosisId);
      const b=document.getElementById("copy-short");
      const prev=b.textContent;
      b.textContent="복사했어요!";
      setTimeout(()=>{ b.textContent=prev; }, 2000);
    };
  }
  if(document.getElementById("copy")){
    document.getElementById("copy").onclick = async ()=>{
      await navigator.clipboard.writeText(copyText);
      postPilotFunnelEvent("pilot_copy_inquiry", diagnosisId);
      const b=document.getElementById("copy");
      const prev=b.textContent;
      b.textContent="복사했어요!";
      setTimeout(()=>{ b.textContent=prev; }, 1500);
    };
  }
  const precOpt = document.getElementById("prec-optional");
  if(precOpt){
    precOpt.onclick = ()=>{ showPrecisionBlocks(false); };
  }
  r.scrollIntoView({behavior:"smooth", block:"start"});
  }catch(e){
    alert(PILOT_COPY.alerts.result_error);
    step = Math.min(step, steps.length - 1);
    stepEl.classList.remove("hidden");
    render();
  }finally{
    submitInFlight = false;
  }
}
bootPilot();
</script></body></html>"""

from admin_ui import ADMIN_HTML  # noqa: E402

SELLER_QUICK_HTML = """<!DOCTYPE html><html lang="ko"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"/>
<title>판매자 빠른 답변</title>
<style>
*{box-sizing:border-box}
body{font-family:system-ui,-apple-system,sans-serif;margin:0;padding:16px;background:#f8fafc;color:#0f172a;font-size:16px;line-height:1.45}
h1{font-size:20px;margin:0 0 6px}
.sub{font-size:13px;color:#64748b;margin:0 0 16px}
label{display:block;font-size:13px;font-weight:600;margin:12px 0 6px}
input[type=text],select,textarea{width:100%;padding:12px;border:1px solid #cbd5e1;border-radius:10px;font-size:16px}
textarea{min-height:120px;resize:vertical}
.fit-row{display:flex;gap:8px;flex-wrap:wrap}
.fit-row label{display:flex;align-items:center;gap:6px;font-weight:500;padding:10px 14px;border:2px solid #e2e8f0;border-radius:10px;background:#fff;cursor:pointer;margin:0}
.fit-row input{position:absolute;opacity:0;width:0;height:0}
.fit-row input:checked+span{font-weight:700;color:var(--pink)}
.fit-row label:has(input:checked){border-color:#f43f5e;background:#fff1f2}
.btn-row{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}
button{padding:12px 16px;border:none;border-radius:10px;font-size:15px;font-weight:600;cursor:pointer}
button.primary{background:#e11d48;color:#fff}
button.secondary{background:#e2e8f0;color:#0f172a}
.card{background:#fff;border-radius:12px;padding:14px;margin:12px 0;border:1px solid #e2e8f0}
.card b{display:block;font-size:18px;margin:4px 0}
.err{color:#b91c1c;font-size:14px;margin:8px 0}
.note{font-size:12px;color:#64748b}
#preview{display:none}
</style></head><body>
<h1>판매자 빠른 답변</h1>
<p class="sub">북마크: <code>/seller/quick?token=...</code> · 진단번호 + 상품 핏 → 카톡/톡톡 문구</p>
<label for="dxCode">진단번호</label>
<input type="text" id="dxCode" placeholder="예: SF01-000001" autocomplete="off"/>
<button type="button" class="secondary" id="btnRecent" style="margin-top:8px;width:100%">최근 진단 불러오기</button>
<div id="err" class="err" style="display:none"></div>
<div id="summary" class="card" style="display:none"></div>
<label>상품 핏 (스마트스토어 옵션)</label>
<div class="fit-row" id="fitRow">
  <label><input type="radio" name="fit" value="기본핏" checked/><span>기본핏</span></label>
  <label><input type="radio" name="fit" value="편한핏"/><span>편한핏</span></label>
  <label><input type="radio" name="fit" value="아주 편한핏"/><span>아주 편한핏</span></label>
</div>
<label for="workStep">발볼 늘림 단계 (비우면 SF 코드 기준 자동)</label>
<select id="workStep">
  <option value="">자동</option>
  <option value="0">0 — 없음</option>
  <option value="1">1단계</option>
  <option value="2">2단계</option>
</select>
<label><input type="checkbox" id="saveMemo"/> 생성 시 실작업·메모 저장 (관리자 DB)</label>
<div class="btn-row">
  <button type="button" class="primary" id="btnGen">답변 생성</button>
</div>
<div id="preview">
  <label>짧은 답변 <button type="button" class="secondary" id="copyShort">복사</button></label>
  <textarea id="outShort" readonly></textarea>
  <label>긴 답변 (톡톡) <button type="button" class="secondary" id="copyLong">복사</button></label>
  <textarea id="outLong" readonly></textarea>
  <label>1회 교환 인증 문구 <button type="button" class="secondary" id="copyEx">복사</button></label>
  <textarea id="outEx" readonly></textarea>
  <p class="note" id="sellerNote"></p>
</div>
<script>
const token = (new URLSearchParams(location.search).get("token") || "").trim();
const h = { "X-Admin-Token": token, "Content-Type": "application/json" };
let currentDx = null;
function showErr(m){ const el=document.getElementById("err"); el.style.display=m?"block":"none"; el.textContent=m||""; }
function fitVal(){ const c=document.querySelector('input[name="fit"]:checked'); return c?c.value:"기본핏"; }
async function loadCode(code){
  showErr("");
  const c=(code||"").trim();
  if(!c){ showErr("진단번호를 입력하세요."); return; }
  const r=await fetch("/api/seller/diagnosis?code="+encodeURIComponent(c)+"&token="+encodeURIComponent(token),{headers:h});
  if(!r.ok){ const e=await r.json().catch(()=>({})); showErr(e.detail||"조회 실패"); document.getElementById("summary").style.display="none"; return; }
  const j=await r.json();
  currentDx=j;
  const s=document.getElementById("summary");
  s.style.display="block";
  s.innerHTML="<b>"+j.diagnosis_code+"</b>"+j.recommendation_code+" · "+j.q4+"mm"
    +(j.product_id?" · "+j.product_id:"")
    +"<small>R/P/S: "+(j.r_code||"-")+"/"+(j.p_code||"-")+"/"+(j.s_code||"-")+"</small>";
  document.getElementById("dxCode").value=j.diagnosis_code;
}
document.getElementById("dxCode").addEventListener("change",()=>loadCode(document.getElementById("dxCode").value));
document.getElementById("btnRecent").onclick=async()=>{
  if(!token){ showErr("관리자 토큰이 없습니다. URL에 ?token=... 을 넣어 주세요."); return; }
  const r=await fetch("/api/admin/diagnoses?token="+encodeURIComponent(token),{headers:h});
  if(!r.ok){
    const e=await r.json().catch(()=>({}));
    const d=(e && (e.detail||e.error)) ? String(e.detail||e.error) : "";
    showErr("최근 목록 실패"+(d?(" ("+d+")"):""));
    return;
  }
  const j=await r.json();
  const items=(j.items||[]).slice(0,8);
  if(!items.length){ showErr("진단 기록이 없습니다."); return; }
  const pick=items[0];
  await loadCode(pick.diagnosis_code);
};
async function copyFrom(id){
  const t=document.getElementById(id);
  try{ await navigator.clipboard.writeText(t.value); }catch(e){ t.select(); document.execCommand("copy"); }
}
document.getElementById("copyShort").onclick=()=>copyFrom("outShort");
document.getElementById("copyLong").onclick=()=>copyFrom("outLong");
document.getElementById("copyEx").onclick=()=>copyFrom("outEx");
document.getElementById("btnGen").onclick=async()=>{
  showErr("");
  const code=document.getElementById("dxCode").value.trim();
  if(!code){ showErr("진단번호를 입력하세요."); return; }
  const ws=document.getElementById("workStep").value;
  const body={ diagnosis_code:code, seller_fit_line:fitVal(), save:document.getElementById("saveMemo").checked };
  if(ws!=="") body.actual_work_step=+ws;
  const r=await fetch("/api/seller/reply",{method:"POST",headers:h,body:JSON.stringify(body)});
  if(!r.ok){ const e=await r.json().catch(()=>({})); showErr(e.detail||"생성 실패"); return; }
  const j=await r.json();
  document.getElementById("preview").style.display="block";
  document.getElementById("outShort").value=j.reply_short||"";
  document.getElementById("outLong").value=j.reply_long||"";
  document.getElementById("outEx").value=j.reply_exchange||"";
  document.getElementById("sellerNote").textContent=j.seller_note?(j.seller_note+" (고객 문구에 넣지 마세요)"):"";
  if(j.diagnosis) currentDx=j.diagnosis;
};
if(!token) showErr("URL에 ?token= 관리자 토큰이 필요합니다.");
</script></body></html>"""

PILOT_BUILD = "20260722-mobile-font"
