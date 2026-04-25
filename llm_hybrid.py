"""
하이브리드 LLM 보조 응답기.

역할:
- 상태머신이 기대한 입력 형식과 다를 때, 자연어 안내 후 현재 단계 복귀 유도
- 설정이 없거나 호출 실패 시 None 반환(규칙형 fallback 유지)
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=False)


class HybridLLMAssistant:
    def __init__(self):
        self.enabled = os.environ.get("HYBRID_LLM_ENABLED", "false").strip().lower() in ("1", "true", "yes", "on")
        self.api_url = os.environ.get("HYBRID_LLM_API_URL", "").strip()
        self.api_key = os.environ.get("HYBRID_LLM_API_KEY", "").strip()
        self.model = os.environ.get("HYBRID_LLM_MODEL", "gpt-4o-mini").strip()
        self.timeout_sec = float(os.environ.get("HYBRID_LLM_TIMEOUT_SEC", "5").strip())

    def reply(
        self,
        user_message: str,
        state: str,
        expected_options: list[str],
        fallback_hint: str = "",
    ) -> str | None:
        if not self.enabled or not self.api_url:
            return None

        system_prompt = (
            "당신은 신발 상담 챗봇 보조 어시스턴트다. "
            "사용자 입력에 짧게 답하고, 반드시 현재 단계 선택지로 복귀시켜라. "
            "규칙: 1) 3문장 이내 2) 과장 금지 3) 마지막 문장은 선택 유도."
        )
        options_text = ", ".join(expected_options) if expected_options else "자유 입력"
        user_prompt = (
            f"현재 상태: {state}\n"
            f"사용자 입력: {user_message}\n"
            f"현재 선택지: {options_text}\n"
            f"파싱 실패 힌트: {fallback_hint}\n\n"
            "요청: 공감형으로 짧게 답한 뒤, 현재 단계에서 어떤 버튼을 눌러야 하는지 안내해줘."
        )

        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = urllib.request.Request(
            self.api_url,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                raw = resp.read().decode("utf-8")
            return self._extract_text(json.loads(raw))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, TypeError, KeyError):
            return None
        except Exception:
            return None

    def _extract_text(self, payload: dict) -> str | None:
        choices = payload.get("choices")
        if isinstance(choices, list) and choices:
            text = choices[0].get("message", {}).get("content")
            if isinstance(text, str) and text.strip():
                return text.strip()

        output = payload.get("output")
        if isinstance(output, list):
            for item in output:
                content = item.get("content")
                if not isinstance(content, list):
                    continue
                for part in content:
                    text = part.get("text")
                    if isinstance(text, str) and text.strip():
                        return text.strip()
        return None
