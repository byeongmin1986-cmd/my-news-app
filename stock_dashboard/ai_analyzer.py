"""
AI-powered stock analysis.
Tries Anthropic Claude first, then OpenAI as fallback.
Returns a structured dict with analysis sections.

⚠️ This is for informational purposes only — not investment advice.
"""

import os
import json
import streamlit as st


_SYSTEM_PROMPT = """당신은 주식 시장 데이터를 분석하는 도우미입니다.
주어진 데이터를 바탕으로 가능한 분석을 제공하되,
절대로 매수/매도를 추천하거나 "확실하다", "반드시" 같은 단정적 표현을 쓰지 마세요.
모든 분석은 참고용이며 실제 투자 결정은 투자자 본인의 책임임을 항상 명심하세요."""


def _build_prompt(ticker: str, info: dict, price: dict, news: list[dict]) -> str:
    change_pct = price.get("change_pct", 0)
    direction = "상승" if change_pct >= 0 else "하락"
    currency = info.get("currency", "USD")
    current = price.get("current", "N/A")
    w52h = price.get("week52_high", "N/A")
    w52l = price.get("week52_low", "N/A")

    price_fmt = f"₩{current:,.0f}" if currency == "KRW" else f"${current:.2f}"
    h_fmt = f"₩{w52h:,.0f}" if (currency == "KRW" and w52h) else (f"${w52h:.2f}" if w52h else "N/A")
    l_fmt = f"₩{w52l:,.0f}" if (currency == "KRW" and w52l) else (f"${w52l:.2f}" if w52l else "N/A")

    news_lines = "\n".join(
        f"- [{n.get('sentiment','neutral').upper()}] {n.get('title', '')}"
        for n in (news or [])[:5]
    ) or "뉴스 데이터 없음"

    return f"""
다음 정보를 분석해 JSON으로만 응답하세요 (추가 텍스트 없이).

【종목】 {info.get('name')} ({ticker})
【현재가】 {price_fmt}
【오늘 변동】 {change_pct:+.2f}% ({direction})
【52주 고점】 {h_fmt}
【52주 저점】 {l_fmt}

【최근 뉴스 헤드라인】
{news_lines}

응답 JSON 형식:
{{
  "bullish_factors": "상승 가능 요인 3-4개를 마크다운 리스트(- 항목)로",
  "bearish_factors": "하락 가능 요인 3-4개를 마크다운 리스트(- 항목)로",
  "risks": "주요 리스크 2-3개를 마크다운 리스트(- 항목)로",
  "market_context": "현재 시장 맥락 2-3문장 설명",
  "beginner_summary": "주식을 처음 보는 사람도 이해할 수 있는 한 줄 해석 (참고용임을 명시)"
}}
"""


def _parse_json(text: str) -> dict | None:
    text = text.strip()
    for wrapper in ["```json", "```"]:
        if wrapper in text:
            text = text.split(wrapper, 1)[1].split("```", 1)[0].strip()
            break
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


# ── Anthropic ────────────────────────────────────────────────────────────────

def _anthropic_analyze(ticker, info, price, news) -> dict | None:
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": _build_prompt(ticker, info, price, news)}],
        )
        return _parse_json(msg.content[0].text)
    except Exception:
        return None


# ── OpenAI ───────────────────────────────────────────────────────────────────

def _openai_analyze(ticker, info, price, news) -> dict | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1024,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": _build_prompt(ticker, info, price, news)},
            ],
        )
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return None


# ── Public interface ──────────────────────────────────────────────────────────

def analyze_with_ai(
    ticker: str,
    ticker_info: dict,
    price_data: dict,
    news_items: list[dict],
) -> dict:
    """
    Run AI analysis. Returns structured dict, or {} if no API key is available.
    Never raises — callers check for empty dict.
    """
    result = _anthropic_analyze(ticker, ticker_info, price_data, news_items)
    if result:
        return result

    result = _openai_analyze(ticker, ticker_info, price_data, news_items)
    if result:
        return result

    return {}
