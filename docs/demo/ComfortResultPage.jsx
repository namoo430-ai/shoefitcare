/**
 * 참고용 React UI (스마트스토어/웹뷰 연동 시).
 * 문구 원본: comfort_result_copy.py
 *
 * props.pain: "hallux" | "wide_ball" | "high_instep" | "edema"
 * props.checkoutPayload: 상품 페이지 query/state 로 전달
 */

import React from "react";

const PAIN_DIAGNOSIS = {
  hallux: `고객님은 엄지발가락 옆뼈가 눌리는 무지외반 유형입니다.

👉 추천 옵션
무지외반은 일반 핏으로는 압박이 쉽게 남습니다.
발 상태에 따라 아래 기준으로 선택해 주세요.
- 기본핏 선택 시 → 와이드 발볼 늘림 필수
- 편한핏 / 와이드핏 제품 → 기본 착용 가능

무지외반이 심한 경우
- 아주편한핏 + 기본늘림
- 편한핏 + 와이드늘림
- 앞코늘림 (필수)

튀어나온 뼈 부분은 발볼만 늘려서는 부족합니다.
앞코까지 함께 확장해야 압박 없이 편하게 신으실 수 있습니다.
이 조합이 아니면 같은 신발도 계속 아프게 느껴질 가능성이 높습니다.`,
  wide_ball: `고객님은 발볼이 넓어 양옆 압박이 있는 유형입니다.

👉 추천 옵션
- 기본핏 + 와이드늘림
- 편한핏 + 기본늘림
- 아주편한핏

신발 형태는 유지하면서 발볼만 자연스럽게 여유를 만들어주는 조합입니다.
가장 많은 고객분들이 선택하는 안정적인 방법입니다.`,
  high_instep: `고객님은 발등이 높아 위쪽 압박을 받는 유형입니다.

👉 추천 옵션
- 편한핏 또는 아주편한핏
- 발등이 높은 경우 → 한 사이즈 크게 선택 추천

이 경우 발볼보다 전체적인 여유가 더 중요합니다.
발볼을 무리하게 늘리기보다 핏으로 해결하는 것이 가장 편합니다.`,
  edema: `고객님은 시간이 지날수록 발이 붓는 유형입니다.

👉 추천 옵션
- 편한핏 또는 아주편한핏
- 발볼늘림 없음

오후 붓는 상태까지 고려해 처음부터 여유 있는 핏을 선택하는 것이 중요합니다.
딱 맞는 신발은 시간이 지나면 불편해질 가능성이 높습니다.`,
};

const WEARING = `이 신발은 발을 부드럽게 감싸주면서 편안하게 신으실 수 있는 여유 있는 착화감입니다.
발볼이 넓거나 오래 걸으면 발이 쉽게 피로해지는 분들께 잘 맞습니다.

✔ 발볼이 넓으신 분 → 발볼늘림 선택 추천
✔ 무지외반이 있으신 분 → 앞코늘림 함께 추천
✔ 발등이 높으신 분 → 한 사이즈 크게 선택 추천

발에 맞게 조정된 신발은 걸을수록 편안함이 더 잘 느껴집니다.
발 모양에 맞춰 조정되는 과정에서 자연스러운 형태 변화가 있을 수 있으며 편안한 착용을 위한 과정입니다.
처음부터 발에 맞게 선택하시면 오래 신을수록 편안함을 더 느끼실 수 있습니다.`;

const TRUST = "비슷한 불편을 느끼신 분들이 많이 선택하신 방법입니다";
const CTA = "이대로 편하게 신기";

const styles = {
  page: { maxWidth: 480, margin: "0 auto", padding: "20px 16px 96px", fontSize: 17, lineHeight: 1.65 },
  section: { marginBottom: 28 },
  pre: { whiteSpace: "pre-wrap", margin: 0 },
  trust: { color: "#555", fontSize: 15, textAlign: "center", margin: "16px 0" },
  cta: {
    position: "fixed",
    left: 0,
    right: 0,
    bottom: 0,
    padding: "12px 16px",
    background: "#fff",
    boxShadow: "0 -4px 12px rgba(0,0,0,0.08)",
  },
  ctaBtn: {
    width: "100%",
    padding: "16px 20px",
    fontSize: 18,
    fontWeight: 600,
    border: "none",
    borderRadius: 12,
    background: "#1f3a8a",
    color: "#fff",
  },
};

export function DiagnosisResultBlock({ pain = "wide_ball" }) {
  const text = PAIN_DIAGNOSIS[pain] || PAIN_DIAGNOSIS.wide_ball;
  return (
    <section style={styles.section}>
      <h2 style={{ fontSize: 19, marginBottom: 12 }}>진단 결과</h2>
      <p style={styles.pre}>{text}</p>
    </section>
  );
}

export function WearingGuidanceSection() {
  return (
    <section style={styles.section}>
      <h2 style={{ fontSize: 19, marginBottom: 12 }}>착화 안내</h2>
      <p style={styles.pre}>{WEARING}</p>
    </section>
  );
}

export function ComfortResultPage({ pain, checkoutPayload, onCheckout }) {
  const handleCta = () => {
    if (onCheckout) onCheckout(checkoutPayload);
  };

  return (
    <div style={styles.page}>
      <DiagnosisResultBlock pain={pain} />
      <WearingGuidanceSection />
      <p style={styles.trust}>{TRUST}</p>
      <div style={styles.cta}>
        <button type="button" style={styles.ctaBtn} onClick={handleCta}>
          {CTA}
        </button>
      </div>
    </div>
  );
}

export default ComfortResultPage;
