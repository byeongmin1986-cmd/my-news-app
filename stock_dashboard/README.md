# 📈 주식 대시보드

초보자도 쉽게 보는 **매일 자동 갱신 주식 분석 앱**.

> ⚠️ **투자 주의사항**: 이 앱은 참고용 정보만 제공합니다. 매수/매도 추천이 아닙니다.

---

## 📌 관심 종목

| 종목 | 설명 |
|------|------|
| **SOXL** | Direxion 반도체 3X 레버리지 ETF |
| **FCEL** | FuelCell Energy (수소 연료전지) |
| **삼성전자** | 코스피 005930.KS |

---

## ✨ 기능

- 현재가 · 등락률 · 52주 고점/저점 · 거래량 카드
- 1일 / 5일 / 1개월 / 6개월 / 1년 인터랙티브 차트 (Plotly)
- 최근 뉴스 + 긍정/부정/중립 감성 분석
- AI 분석 (Claude 또는 GPT): 상승/하락 가능 이유, 리스크, 초보자용 한 줄 해석
- 데이터 6시간 캐시 (앱 재접속 시 자동 갱신)
- 모바일 반응형 UI

---

## 🚀 빠른 시작

### 1. Python 환경 준비

Python 3.11 이상을 권장합니다.

```bash
# 가상환경 생성 (선택 사항이지만 권장)
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 2. 패키지 설치

```bash
cd stock_dashboard
pip install -r requirements.txt
```

### 3. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 API 키를 입력하세요:

```env
ANTHROPIC_API_KEY=sk-ant-...   # Claude AI 분석 (권장)
FINNHUB_API_KEY=...             # 뉴스 강화 (선택)
```

> **API 키 없이도 실행 가능합니다.** 뉴스는 Google News RSS로, AI 분석 섹션은 안내 메시지로 대체됩니다.

### 4. 앱 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 로 접속하세요.

---

## 🔑 API 키 발급 방법

### Anthropic Claude (AI 분석 - 권장)
1. [console.anthropic.com](https://console.anthropic.com) 가입
2. API Keys 메뉴 → Create Key
3. `.env`에 `ANTHROPIC_API_KEY=...` 입력

### Finnhub (미국 주식 뉴스 - 무료 플랜 있음)
1. [finnhub.io](https://finnhub.io) 가입
2. Dashboard에서 API Key 복사
3. `.env`에 `FINNHUB_API_KEY=...` 입력

---

## 📂 파일 구조

```
stock_dashboard/
├── app.py              ← 메인 Streamlit 앱
├── data_cache.py       ← 주가 데이터 (yfinance + 6시간 캐시)
├── news_fetcher.py     ← 뉴스 (Finnhub / Google News RSS)
├── ai_analyzer.py      ← AI 분석 (Claude / GPT)
├── requirements.txt    ← 패키지 목록
├── .env.example        ← 환경 변수 템플릿
├── .streamlit/
│   └── config.toml     ← 다크 테마 설정
└── README.md           ← 이 파일
```

---

## ☁️ Streamlit Cloud 배포

1. GitHub에 이 저장소를 푸시
2. [share.streamlit.io](https://share.streamlit.io) 에서 앱 생성
   - Main file path: `stock_dashboard/app.py`
3. **Settings → Secrets** 에 `.env` 내용 붙여넣기:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
FINNHUB_API_KEY = "..."
```

---

## ⚙️ GitHub Actions 자동 갱신

`.github/workflows/daily_refresh.yml` 파일을 사용하면 매일 오전 9시(KST)에  
Streamlit Cloud 앱을 자동으로 깨워 최신 데이터를 준비시킬 수 있습니다.

---

## 🛠️ 문제 해결

| 증상 | 해결 방법 |
|------|-----------|
| 주가가 표시 안 됨 | 인터넷 연결 확인. 장 마감 후 데이터가 없을 수 있음 |
| 뉴스가 안 보임 | Google News RSS는 국가/IP에 따라 차단될 수 있음. Finnhub 키 추가 권장 |
| AI 분석 오류 | `.env`의 API 키 확인. Claude 키 잔액 확인 |
| 삼성전자 차트 오류 | KRX는 당일 데이터(5m)가 제한적. 1일 이상 기간 선택 시 정상 표시됨 |
| `ModuleNotFoundError` | `pip install -r requirements.txt` 재실행 |

---

## ⚠️ 면책 조항

이 앱은 교육 및 정보 제공 목적으로만 만들어졌습니다.  
주식 투자에는 원금 손실 위험이 있으며, 이 앱의 정보로 인한 투자 손실에 대해 책임지지 않습니다.  
투자 전 반드시 본인이 충분히 공부하고, 필요하면 전문 금융 상담사에게 조언을 구하세요.
