# 🖥️ 사하라 이남 아프리카 데스크탑 모니터 가격 추적기

케냐, 가나, 나이지리아 등 아프리카 주요 온라인 쇼핑몰에서 데스크탑 모니터 가격을 매주 자동으로 수집하고 비교하는 앱입니다.

## 📁 폴더 구조

```
monitor_tracker/
├── config/
│   └── settings.py          # 사이트 URL, 딜레이, 브랜드 설정
├── database/
│   ├── models.py            # DB 테이블 스키마
│   └── db_manager.py       # DB 읽기/쓰기 함수
├── utils/
│   ├── normalizer.py        # 브랜드명, 상태 정규화
│   └── extractor.py        # 화면 크기, 해상도, 주사율 추출
├── scrapers/
│   ├── base_scraper.py     # 공통 기반 클래스 (모든 scraper가 상속)
│   ├── kenya/
│   │   └── jumia_ke.py     # Jumia Kenya 크롤러
│   ├── ghana/
│   │   └── compughana.py   # CompuGhana 크롤러
│   └── nigeria/
│       └── jumia_ng.py     # Jumia Nigeria 크롤러
├── dashboard/
│   └── app.py              # Streamlit 대시보드
├── data/                   # SQLite DB 저장 위치
├── logs/                   # 크롤링 로그
├── exports/                # CSV/Excel 내보내기
├── main.py                 # 실행 진입점
└── requirements.txt
```

## ⚡ 빠른 시작

### 1단계: Python 설치 확인

```bash
python --version   # Python 3.10 이상 필요
```

> Python이 없으면 https://www.python.org/downloads/ 에서 설치

### 2단계: 저장소 클론 및 이동

```bash
git clone https://github.com/YOUR_USERNAME/my-news-app.git
cd my-news-app/monitor_tracker
```

### 3단계: 가상환경 생성 (권장)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python -m venv venv
source venv/bin/activate
```

### 4단계: 패키지 설치

```bash
pip install -r requirements.txt
```

### 5단계: Playwright 브라우저 설치 (선택사항)

현재 MVP는 `requests` + `BeautifulSoup` 방식을 사용하므로 필수는 아닙니다.
JS 렌더링이 필요한 사이트를 추가할 때 설치하세요.

```bash
playwright install chromium
```

### 6단계: 크롤러 실행

```bash
# monitor_tracker 폴더 안에서 실행
cd monitor_tracker

# 모든 사이트 크롤링
python main.py

# 특정 국가만
python main.py --country kenya

# 특정 사이트만
python main.py --site compughana

# 테스트 (DB 저장 없이 결과만 출력)
python main.py --dry-run
```

### 7단계: 대시보드 실행

```bash
streamlit run dashboard/app.py
```

브라우저에서 http://localhost:8501 로 접속하면 대시보드가 열립니다.

## 🔧 설정 변경

`config/settings.py` 파일에서 아래 항목을 수정할 수 있습니다:

| 항목 | 설명 | 기본값 |
|------|------|--------|
| `delay_min` | 요청 간 최소 딜레이 (초) | 2 |
| `delay_max` | 요청 간 최대 딜레이 (초) | 5 |
| `max_pages` | 사이트당 최대 페이지 수 | 10 |
| `max_retries` | 실패 시 재시도 횟수 | 3 |
| `timeout` | 요청 타임아웃 (초) | 30 |

## ➕ 새 사이트 추가 방법

새 사이트(예: Jiji Kenya)를 추가하는 방법:

### 1. scraper 파일 생성

```bash
# 예시: Kenya의 jiji.co.ke 추가
touch scrapers/kenya/jiji_ke.py
```

`scrapers/kenya/jiji_ke.py` 내용:

```python
from scrapers.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)

# 이 딕셔너리만 수정하면 사이트 구조 변경에 대응
SELECTORS = {
    "product_list": "div.masonry-item",  # 실제 선택자로 교체
    "title": "div.qa-advert-title",
    "price": "div.qa-advert-price",
    "link": "a.b-advert-title-inner",
    "image": "img.b-advert-thumbnail",
}

class JijiKenyaScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            country="Kenya",
            retailer="Jiji Kenya",
            base_url="https://jiji.co.ke",
            currency="KES",
        )

    def scrape(self) -> list[dict]:
        products = []
        url = f"{self.base_url}/search?query=monitor"
        soup = self.fetch(url)
        if soup:
            for item in soup.select(SELECTORS["product_list"]):
                # 파싱 로직 작성
                title_tag = item.select_one(SELECTORS["title"])
                title = title_tag.get_text(strip=True) if title_tag else ""
                if not title or not self.is_monitor_product(title):
                    continue
                # ... 나머지 필드 추출
                products.append(self.build_product(
                    product_title=title,
                    # ...
                ))
        return products
```

### 2. settings.py에 등록

```python
# config/settings.py의 SITES 딕셔너리에 추가
SITES = {
    "kenya": {
        "jumia_ke": { ... },  # 기존
        "jiji_ke": {          # 새로 추가
            "enabled": True,
            "retailer": "Jiji Kenya",
            "base_url": "https://jiji.co.ke",
            "currency": "KES",
            "module": "scrapers.kenya.jiji_ke",
            "class": "JijiKenyaScraper",
        }
    },
}
```

완료! 이제 `python main.py --site jiji_ke`로 실행 가능합니다.

## ⏰ 자동 실행 설정

### GitHub Actions (권장)

1. `.github/workflows/weekly_scraper.yml` 이 이미 포함되어 있습니다.
2. 저장소를 GitHub에 push하면 매주 월요일 오전 6시 UTC에 자동 실행됩니다.
3. Actions 탭에서 수동 실행도 가능합니다 (Workflow dispatch).

### cron (서버/로컬)

```bash
# crontab -e 로 편집
# 매주 월요일 오전 9시 (한국 시간 기준)
0 9 * * 1 cd /path/to/my-news-app/monitor_tracker && python main.py >> logs/cron.log 2>&1
```

## 📊 수집 데이터 필드

| 필드 | 설명 | 예시 |
|------|------|------|
| `country` | 국가명 | Kenya |
| `retailer` | 쇼핑몰 이름 | Jumia Kenya |
| `product_title` | 상품명 | HP 24f 23.8 inch FHD Monitor |
| `brand` | 브랜드 (정규화) | HP |
| `model` | 모델 번호 | 24F |
| `screen_size_inch` | 화면 크기 | 23.8 |
| `resolution` | 해상도 | 1920x1080 |
| `refresh_rate` | 주사율 (Hz) | 60 |
| `panel_type` | 패널 종류 | IPS |
| `condition` | 상태 | new / used / refurbished |
| `price` | 가격 (숫자) | 15000 |
| `currency` | 통화 | KES |
| `availability` | 재고 상태 | in stock |
| `product_url` | 상품 링크 | https://... |
| `image_url` | 이미지 링크 | https://... |
| `crawl_date` | 수집 날짜 | 2024-01-15 |

## 🚨 주의사항

- **robots.txt 준수**: 각 사이트의 robots.txt 규칙을 자동으로 확인하고 허용된 URL만 크롤링합니다.
- **요청 딜레이**: 기본 2~5초 딜레이로 서버에 무리를 주지 않습니다.
- **개인 사용 목적**: 수집한 데이터는 개인 분석 목적으로만 사용하세요.
- **사이트 구조 변경**: 사이트 HTML 구조가 바뀌면 해당 scraper 파일의 `SELECTORS` 딕셔너리만 수정하세요.

## 🛠️ 문제 해결

### "No products found" 오류
→ 사이트 HTML 구조가 변경됐을 수 있습니다. 브라우저 개발자 도구(F12)로 실제 선택자를 확인하고 SELECTORS를 업데이트하세요.

### DB 위치
→ `monitor_tracker/data/monitors.db`

### 로그 확인
→ `monitor_tracker/logs/` 폴더의 최신 `.log` 파일 확인

### 패키지 충돌
```bash
pip install --upgrade -r requirements.txt
```

## 🗺️ 향후 계획

- [ ] Tanzania: jiji.co.tz, beichee.co.tz
- [ ] Ethiopia: jiji.com.et  
- [ ] Uganda: jiji.ug, abanista.com
- [ ] Ghana: jumia.com.gh, jiji.com.gh
- [ ] Nigeria: konga.com, slot.ng, jiji.ng
- [ ] Senegal: ubuy.sn, expat-dakar.com
- [ ] 환율 API 연동으로 USD 기준 비교
- [ ] 가격 알림 (이메일/Slack)
- [ ] PostgreSQL 마이그레이션
