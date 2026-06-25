import { Complex } from './types';

// ⚠️ 모든 가격 및 사업 단계 정보는 공개된 자료를 바탕으로 작성되었으나,
//    실거래 시 반드시 국토교통부 실거래가 공개시스템 및 각 구청/조합 공식 자료로 재확인이 필요합니다.

export const COMPLEXES: Complex[] = [
  // ─── 현재 보유 ─────────────────────────────────────────────────
  {
    id: 'indukwon-samsung',
    name: '인덕원마을삼성아파트',
    shortName: '인덕원삼성',
    type: 'current',

    location: {
      address: '경기도 안양시 동안구 관양동',
      district: '안양시 동안구',
      neighborhood: '관양동',
      lat: 37.3896,
      lng: 126.9609,
      subwayStations: [
        { name: '인덕원역', line: '4호선', walkMinutes: 10 },
      ],
      nearbySchools: [
        { name: '관양중학교', type: '중', distanceM: 500 },
        { name: '안양고등학교', type: '고', distanceM: 800 },
      ],
      nearbyFeatures: ['인덕원역 인근', '평촌학원가 접근 가능', '수리산 도립공원'],
    },

    basicInfo: {
      builtYear: 1996,
      totalUnits: 1002,
      floorAreaRatio: 220,
      buildingCoverage: 22,
      avgLandShare: 12,
      verified: false,
    },

    prices: {
      current24py: 116000,
      current34py: 155000,
      current42py: 195000,
      recentTransactionDate: '2026-06',
      highestPrice24py: 125000,
      highestPriceDate: '2021-10',
      recoveryRate: 93,
      priceHistory: [
        { date: '2020-01', price24py: 75000 },
        { date: '2020-07', price24py: 83000 },
        { date: '2021-01', price24py: 95000 },
        { date: '2021-07', price24py: 115000 },
        { date: '2022-01', price24py: 122000 },
        { date: '2022-07', price24py: 118000 },
        { date: '2023-01', price24py: 108000 },
        { date: '2023-07', price24py: 110000 },
        { date: '2024-01', price24py: 113000 },
        { date: '2024-07', price24py: 114000 },
        { date: '2025-01', price24py: 115000 },
        { date: '2026-06', price24py: 116000 },
      ],
      verified: false,
      dataSource: 'KB부동산 시세 참고 (2026.06 기준 11.6억). 국토부 실거래가 공개시스템 재확인 권장',
    },

    reconstruction: {
      stage: '리모델링 추진 중',
      stageCode: 2,
      stageDetail: '리모델링 사업 검토 단계 — 재건축 제외 대상',
      associationEstablished: false,
      businessApprovalDate: '',
      managementDisposalDate: '',
      relocationCompleted: false,
      constructionStarted: false,
      expectedCompletion: '미정 (리모델링 추진)',
      expectedUnitsAfter: 1100,
      expectedFARAfter: 250,
      generalSaleUnits: 0,
      contractor: '미정',
      expectedBrand: '미정',
      profitabilityNotes: '리모델링의 경우 재건축 대비 시세 상승 폭이 제한적',
      verified: false,
      dataSource: '확인 필요',
    },

    scores: {
      location: 58,
      school: 62,
      transport: 60,
      profitability: 35,
      risk: 45,
      overall: 52,
      investmentAttractiveness: 38,
      livingComfort: 65,
    },

    pros: [
      '인덕원역(4호선) 도보 10분 접근',
      '평촌 학원가 인근',
      '현재 보유 — 이사 없이 유지 가능',
      '준수한 주거 환경',
    ],
    cons: [
      '리모델링 추진 중 — 재건축 대비 시세 상승 폭 제한',
      '서울 핵심 입지가 아님',
      '장기 자산 가치 상승 동력 약함',
      '재건축 완료 후에도 브랜드 프리미엄 낮음',
    ],
    risks: [
      '리모델링 사업 무산 시 노후화 리스크',
      '인덕원~서울 접근성 상대적 열위',
    ],
    wifePersuasionPoints: [],
    recommendationRank: 0,
    recommendationSummary: '현재 보유 자산 — 비교 기준점',
  },

  // ─── 1. 일원가람아파트 ──────────────────────────────────────────
  {
    id: 'ilwon-garam',
    name: '일원가람아파트',
    shortName: '일원가람',
    type: 'target',
    comparePy: 27,

    location: {
      address: '서울 강남구 일원동 735',
      district: '강남구',
      neighborhood: '일원동',
      lat: 37.4882,
      lng: 127.0685,
      subwayStations: [
        { name: '일원역', line: '수인분당선', walkMinutes: 7 },
        { name: '대청역', line: '3호선', walkMinutes: 15 },
      ],
      nearbySchools: [
        { name: '일원초등학교', type: '초', distanceM: 300 },
        { name: '개원중학교', type: '중', distanceM: 500 },
        { name: '중동고등학교', type: '고', distanceM: 700 },
      ],
      nearbyFeatures: [
        '수인분당선 일원역 역세권',
        '대치동 학원가 차량 10분',
        '강남세브란스병원 인근',
        '탄천 산책로 인접',
        '개포·일원 재건축 벨트',
        '삼성서울병원 인근',
      ],
    },

    basicInfo: {
      builtYear: 1993,
      totalUnits: 496,
      floorAreaRatio: 109,
      buildingCoverage: 20,
      avgLandShare: 22,
      verified: false,
    },

    prices: {
      current24py: 215000,
      current27py: 270000,
      current34py: 345000,
      current42py: 430000,
      recentTransactionDate: '2025-06',
      highestPrice24py: 264000,
      highestPrice27py: 330000,
      highestPriceDate: '2022-01',
      recoveryRate: 82,
      priceHistory: [
        { date: '2020-01', price24py: 140000, price27py: 175000 },
        { date: '2020-07', price24py: 164000, price27py: 205000 },
        { date: '2021-01', price24py: 204000, price27py: 255000 },
        { date: '2021-07', price24py: 244000, price27py: 305000 },
        { date: '2022-01', price24py: 264000, price27py: 330000 },
        { date: '2022-07', price24py: 232000, price27py: 290000 },
        { date: '2023-01', price24py: 192000, price27py: 240000 },
        { date: '2023-07', price24py: 194000, price27py: 242000 },
        { date: '2024-01', price24py: 198000, price27py: 248000 },
        { date: '2024-07', price24py: 206000, price27py: 258000 },
        { date: '2025-03', price24py: 222000, price27py: 278000 },
        { date: '2025-06', price24py: 216000, price27py: 270000 },
      ],
      verified: false,
      dataSource: '실거래 기반 (2025.03 27평 실거래 27.8억, 3개월 시세 25.4억 참고). 국토부 실거래가 공개시스템 재확인 권장',
    },

    reconstruction: {
      stage: '정비구역 지정 추진',
      stageCode: 2,
      stageDetail: '2024년 6월 예비안전진단 통과. 강남구 정비계획 결정 및 정비구역 지정 주민공람 진행 중. 재건축 후 828가구(임대 77 포함) 예정',
      associationEstablished: false,
      businessApprovalDate: '',
      managementDisposalDate: '',
      relocationCompleted: false,
      constructionStarted: false,
      expectedCompletion: '2033년 이후 (확인 필요)',
      expectedUnitsAfter: 828,
      expectedFARAfter: 300,
      generalSaleUnits: 280,
      contractor: '미정',
      expectedBrand: '미정 (대형 브랜드 유치 기대)',
      profitabilityNotes: '용적률 109% → 재건축 시 300%+로 상향 가능. 5층 저층 → 고층 아파트 변신. 기존 496세대 → 828세대로 증가 (일반분양 약 280세대 예상). 강남구 내 최상급 재건축 수익성',
      verified: false,
      dataSource: '한국경제 2025.08.11 기사 (828가구 탈바꿈), 예비안전진단 통과 확인',
    },

    scores: {
      location: 97,
      school: 92,
      transport: 78,
      profitability: 95,
      risk: 65,
      overall: 90,
      investmentAttractiveness: 95,
      livingComfort: 82,
    },

    pros: [
      '강남구 일원동 — 서울 최고급 주거지',
      '용적률 109% → 재건축 수익성 단연 최상 (5층→고층 변신)',
      '대치동 학원가 차량 10분 — 강남 학군 수혜',
      '828가구 재건축 예정 — 일반분양 약 280세대로 사업성 확인',
      '전세 끼면 갭 약 21억으로 진입 가능',
      '강남세브란스·삼성서울병원 인근 — 의료 인프라 최상',
    ],
    cons: [
      '현 매수가 약 29억 — 자기자본 대비 초과분 해소 필요',
      '현재 5층 저층 — 재건축 완료 전 거주 환경 제한적',
      '수인분당선만 역세권 (강남 접근에 3호선 환승 필요)',
      '재건축 초기 단계 (정비구역 지정 추진) — 완료까지 10년 이상',
      '갭투자 형태 필요 — 실거주 시 자금 부담 더 큼',
    ],
    risks: [
      '정비구역 지정 지연 또는 사업성 재검토 가능성',
      '강남 부동산 규제 변화 (투기과열구역 등) 영향',
      '전세 끼고 매수 시 임차인 갱신청구권 리스크',
      '재건축 초과이익 환수제 부담 높을 수 있음 (강남 지역 특성)',
    ],
    wifePersuasionPoints: [
      '강남구 — 대한민국 교육·인프라 최고 주거지',
      '대치 학원가 차량 10분 — 아이 교육 걱정 없음',
      '강남세브란스·삼성서울병원 바로 근처 — 의료 안심',
      '재건축 완료 후 강남 신축 아파트 거주 — 삶의 질 최상',
    ],
    recommendationRank: 1,
    recommendationSummary: '강남구 최고 입지 + 용적률 109% 재건축 수익성 최강. 자금 확보 가능하면 단연 1순위 — 전세 끼면 갭 약 21억',
  },

  // ─── 2. 올림픽훼밀리타운 ────────────────────────────────────────
  {
    id: 'olympic-family',
    name: '올림픽훼밀리타운',
    shortName: '올림픽훼밀리',
    type: 'target',

    location: {
      address: '서울 송파구 방이동 88번지 일대',
      district: '송파구',
      neighborhood: '방이동',
      lat: 37.5154,
      lng: 127.1236,
      subwayStations: [
        { name: '방이역', line: '5호선', walkMinutes: 5 },
        { name: '올림픽공원역', line: '5호선·9호선', walkMinutes: 10 },
      ],
      nearbySchools: [
        { name: '방이초등학교', type: '초', distanceM: 300 },
        { name: '방산중학교', type: '중', distanceM: 500 },
        { name: '한영고등학교', type: '고', distanceM: 700 },
      ],
      nearbyFeatures: [
        '올림픽공원 인접 (88만m² 녹지)',
        '잠실 생활권',
        '방이 먹자골목',
        '석촌호수 인근',
        '강동·강남 업무지구 접근',
        '롯데월드몰 인근',
      ],
    },

    basicInfo: {
      builtYear: 1988,
      totalUnits: 4494,
      floorAreaRatio: 183,
      buildingCoverage: 21,
      avgLandShare: 14,
      verified: false,
    },

    prices: {
      current24py: 170000,
      current32py: 215000,
      current34py: 228000,
      current42py: 290000,
      recentTransactionDate: '2026-06',
      highestPrice24py: 205000,
      highestPrice32py: 260000,
      highestPriceDate: '2021-11',
      recoveryRate: 83,
      priceHistory: [
        { date: '2020-01', price24py: 105000, price32py: 133000 },
        { date: '2020-07', price24py: 125000, price32py: 158000 },
        { date: '2021-01', price24py: 155000, price32py: 196000 },
        { date: '2021-07', price24py: 190000, price32py: 240000 },
        { date: '2022-01', price24py: 205000, price32py: 260000 },
        { date: '2022-07', price24py: 185000, price32py: 234000 },
        { date: '2023-01', price24py: 160000, price32py: 202000 },
        { date: '2023-07', price24py: 163000, price32py: 206000 },
        { date: '2024-01', price24py: 165000, price32py: 208000 },
        { date: '2024-07', price24py: 168000, price32py: 212000 },
        { date: '2025-01', price24py: 170000, price32py: 213000 },
        { date: '2026-06', price24py: 170000, price32py: 215000 },
      ],
      verified: false,
      dataSource: '웹서치 기반 (2025.06 기준 84㎡ 약 21.5억). 국토부 실거래가 공개시스템 재확인 권장',
    },

    reconstruction: {
      stage: '정비구역 지정 추진',
      stageCode: 2,
      stageDetail: '예비안전진단 통과 후 정비구역 지정 신청 단계 — 정확한 현황 확인 필요',
      associationEstablished: false,
      businessApprovalDate: '',
      managementDisposalDate: '',
      relocationCompleted: false,
      constructionStarted: false,
      expectedCompletion: '2035년 이후 (확인 필요)',
      expectedUnitsAfter: 7000,
      expectedFARAfter: 300,
      generalSaleUnits: 2200,
      contractor: '미정 (대형 건설사 복수 참여 가능성)',
      expectedBrand: '래미안·힐스테이트 등 대형 브랜드 (미확정)',
      profitabilityNotes: '4,494세대 대단지 — 일반분양 규모 크나 사업 기간 장기화 가능성',
      verified: false,
      dataSource: '확인 필요 (서울시 정비사업 정보몽땅, 송파구청 공식 자료 재확인 권장)',
    },

    scores: {
      location: 92,
      school: 85,
      transport: 90,
      profitability: 72,
      risk: 55,
      overall: 84,
      investmentAttractiveness: 82,
      livingComfort: 90,
    },

    pros: [
      '서울 최대 단지급 (4,494세대) — 재건축 후 랜드마크 기대',
      '올림픽공원 바로 옆 — 희귀한 대형 녹지 인접',
      '5호선·9호선 더블역세권 인근',
      '잠실 생활권 — 롯데월드·석촌호수 도보권',
      '방이동 학군 우수',
      '재건축 완료 후 일반분양 규모 대형 — 조합원 이익 기대',
    ],
    cons: [
      '현재 시세가 높아 17억 자기자본으로 추가 대출 필요 (약 1~3억)',
      '4,494세대 대단지 — 조합원 간 이해관계 복잡, 사업 장기화 가능',
      '재건축 완료까지 10년 이상 소요 예상',
      '현재 노후 단지 — 재건축 전 거주 환경 불편 가능',
    ],
    risks: [
      '대규모 단지 특성상 조합 내부 갈등 및 사업 지연 리스크',
      '재건축 완료 전 장기 거주 불편',
      '추가 정부 규제(재건축 초과이익 환수제 등) 변수',
      '현재가 전고점 대비 88% 수준 — 단기 추가 하락 가능성',
    ],
    wifePersuasionPoints: [
      '올림픽공원 바로 옆 — 아이와 산책·운동할 수 있는 녹지 88만m²',
      '잠실 롯데월드·석촌호수 도보권 — 주말 나들이 걸어서 해결',
      '서울 최대급 단지 재건축 — 완공 후 서울에서 가장 주목받는 아파트 중 하나',
      '5호선·9호선 더블역세권 — 어디든 편리하게',
    ],
    recommendationRank: 2,
    recommendationSummary: '입지·브랜드 기대감 우수. 사업 기간 길지만 장기 보유시 최대 기대수익',
  },

  // ─── 2. 가락현대1차 ─────────────────────────────────────────────
  {
    id: 'garak-hyundai1',
    name: '가락현대1차아파트',
    shortName: '가락현대1차',
    type: 'target',

    location: {
      address: '서울 송파구 문정동 3번지 일원',
      district: '송파구',
      neighborhood: '문정동',
      lat: 37.4997,
      lng: 127.1228,
      subwayStations: [
        { name: '가락시장역', line: '8호선', walkMinutes: 5 },
        { name: '송파역', line: '8호선', walkMinutes: 8 },
      ],
      nearbySchools: [
        { name: '가락초등학교', type: '초', distanceM: 400 },
        { name: '가락중학교', type: '중', distanceM: 600 },
        { name: '거원중학교', type: '중', distanceM: 500 },
      ],
      nearbyFeatures: [
        '가락시장 인근',
        '헬리오시티(9,510세대) 바로 인접',
        '문정 법조타운 업무지구',
        '성내천·탄천 인근',
        '가락몰(복합쇼핑몰)',
      ],
    },

    basicInfo: {
      builtYear: 1984,
      totalUnits: 514,
      floorAreaRatio: 179,
      buildingCoverage: 15,
      avgLandShare: 16,
      verified: false,
    },

    prices: {
      current24py: 112000,
      current32py: 140000,
      current34py: 155000,
      current42py: 210000,
      recentTransactionDate: '2025-08',
      highestPrice24py: 155000,
      highestPrice32py: 195000,
      highestPriceDate: '2022-01',
      recoveryRate: 72,
      priceHistory: [
        { date: '2020-01', price24py: 64000, price32py: 80000 },
        { date: '2020-07', price24py: 80000, price32py: 100000 },
        { date: '2021-01', price24py: 112000, price32py: 140000 },
        { date: '2021-07', price24py: 144000, price32py: 180000 },
        { date: '2022-01', price24py: 156000, price32py: 195000 },
        { date: '2022-07', price24py: 136000, price32py: 170000 },
        { date: '2023-01', price24py: 112000, price32py: 140000 },
        { date: '2023-07', price24py: 110000, price32py: 138000 },
        { date: '2024-01', price24py: 109000, price32py: 136000 },
        { date: '2024-07', price24py: 110000, price32py: 138000 },
        { date: '2025-01', price24py: 111000, price32py: 139000 },
        { date: '2025-08', price24py: 112000, price32py: 140000 },
      ],
      verified: false,
      dataSource: '실거래 기반 (84㎡ 평균 약 14억, 123㎡ 2025.07 약 17.5억 확인). 국토부 실거래가 공개시스템 재확인 권장',
    },

    reconstruction: {
      stage: '사업시행인가',
      stageCode: 5,
      stageDetail: '사업시행계획인가 완료, 시공사 입찰 흥행 (롯데건설 등 6개사 참여, 공사비 4,015억원). 842세대로 재건축 예정',
      associationEstablished: true,
      businessApprovalDate: '2024년 (확인 필요)',
      managementDisposalDate: '',
      relocationCompleted: false,
      constructionStarted: false,
      expectedCompletion: '2030년 이후 (확인 필요)',
      expectedUnitsAfter: 842,
      expectedFARAfter: 280,
      generalSaleUnits: 328,
      contractor: '입찰 중 (롯데건설 등 경합)',
      expectedBrand: '미정 (대형 브랜드 확정 예정)',
      profitabilityNotes: '사업시행인가 완료 → 재건축 속도 빠름. 842세대(분양 717+임대 125), 44㎡~168㎡ 다양한 면적 계획',
      verified: false,
      dataSource: '뉴스 기반 (2025.02 시공사 입찰 흥행 확인). 서울시 정비사업 정보몽땅 재확인 권장',
    },

    scores: {
      location: 82,
      school: 78,
      transport: 85,
      profitability: 78,
      risk: 42,
      overall: 79,
      investmentAttractiveness: 80,
      livingComfort: 78,
    },

    pros: [
      '8호선 가락시장역 도보 5분 — 교통 우수',
      '헬리오시티(9,510세대) 바로 인접 — 주변 인프라 최상급',
      '문정 법조타운 업무지구 인근',
      '632세대 적정 규모 — 사업 진행 속도 빠를 수 있음',
      '대지지분 16평 — 사업성 양호',
      '전고점 대비 85% — 추가 상승 여력',
    ],
    cons: [
      '가락시장 특성상 주변 소음·혼잡 가능',
      '재건축 완료까지 약 8~10년 예상',
      '현재 입주 환경 노후화',
    ],
    risks: [
      '가락시장 개발 계획에 따라 주변 환경 변화 가능성',
      '조합설립 단계 — 구체적 진행 상황 재확인 필요',
      '헬리오시티 인접이 경쟁 단지가 될 수도 있음',
    ],
    wifePersuasionPoints: [
      '헬리오시티 옆 — 완공 후 서울 최대 주거단지 생활권 편입',
      '8호선으로 강남 접근 직통 — 출퇴근 편리',
      '문정 법조타운·롯데몰 문정 인근 — 쇼핑·업무 편의시설 완비',
    ],
    recommendationRank: 3,
    recommendationSummary: '교통·입지 균형 우수. 사업시행인가 완료로 속도 빠름. 예산 내 진입 가능성 높음',
  },

  // ─── 3. 가락미륭아파트 ──────────────────────────────────────────
  {
    id: 'garak-mirung',
    name: '가락미륭아파트',
    shortName: '가락미륭',
    type: 'target',

    location: {
      address: '서울 송파구 가락동',
      district: '송파구',
      neighborhood: '가락동',
      lat: 37.5003,
      lng: 127.1208,
      subwayStations: [
        { name: '가락시장역', line: '8호선', walkMinutes: 7 },
        { name: '송파역', line: '8호선', walkMinutes: 6 },
      ],
      nearbySchools: [
        { name: '가락초등학교', type: '초', distanceM: 350 },
        { name: '가락중학교', type: '중', distanceM: 550 },
      ],
      nearbyFeatures: [
        '헬리오시티 인근',
        '가락시장 인근',
        '성내천 인근',
      ],
    },

    basicInfo: {
      builtYear: 1986,
      totalUnits: 435,
      floorAreaRatio: 198,
      buildingCoverage: 26,
      avgLandShare: 17,
      verified: false,
    },

    prices: {
      current24py: 106000,
      current32py: 133000,
      current34py: 140000,
      current42py: 175000,
      recentTransactionDate: '2025-03',
      highestPrice24py: 140000,
      highestPrice32py: 175000,
      highestPriceDate: '2022-01',
      recoveryRate: 76,
      priceHistory: [
        { date: '2020-01', price24py: 58000, price32py: 72000 },
        { date: '2020-07', price24py: 70000, price32py: 88000 },
        { date: '2021-01', price24py: 92000, price32py: 115000 },
        { date: '2021-07', price24py: 126000, price32py: 158000 },
        { date: '2022-01', price24py: 140000, price32py: 175000 },
        { date: '2022-07', price24py: 126000, price32py: 158000 },
        { date: '2023-01', price24py: 96000, price32py: 120000 },
        { date: '2023-07', price24py: 97000, price32py: 122000 },
        { date: '2024-01', price24py: 99000, price32py: 124000 },
        { date: '2024-07', price24py: 102000, price32py: 128000 },
        { date: '2025-01', price24py: 104000, price32py: 130000 },
        { date: '2025-03', price24py: 106000, price32py: 133000 },
      ],
      verified: false,
      dataSource: '실거래 기반 (2025.03 83.58㎡ 실거래 13.3억 확인). 국토부 실거래가 공개시스템 재확인 권장',
    },

    reconstruction: {
      stage: '사업시행인가',
      stageCode: 5,
      stageDetail: '2025년 3월 사업시행계획 인가 완료 (가락미륭·극동·프라자 통합). 기존 435세대 포함 통합 재건축 진행',
      associationEstablished: true,
      businessApprovalDate: '2025-03',
      managementDisposalDate: '',
      relocationCompleted: false,
      constructionStarted: false,
      expectedCompletion: '2031년 이후 (확인 필요)',
      expectedUnitsAfter: 600,
      expectedFARAfter: 280,
      generalSaleUnits: 150,
      contractor: '미정',
      expectedBrand: '미정',
      profitabilityNotes: '435세대 → 가락극동·프라자와 통합 재건축. 대지지분 17평 양호. 2025.03 사업시행인가로 속도 빨라짐',
      verified: false,
      dataSource: '뉴스 기반 (2025.03 통합 사업시행인가 확인). 서울시 정비사업 정보몽땅 재확인 권장',
    },

    scores: {
      location: 80,
      school: 75,
      transport: 82,
      profitability: 70,
      risk: 52,
      overall: 73,
      investmentAttractiveness: 72,
      livingComfort: 72,
    },

    pros: [
      '대지지분 17평 — 가락동 내 양호한 사업성',
      '8호선 송파역·가락시장역 더블 접근',
      '헬리오시티 생활권 공유',
      '현재 매수가 상대적으로 낮아 진입 부담 적음',
    ],
    cons: [
      '292세대 소규모 — 재건축 시 브랜드·규모 기대감 제한',
      '사업 초기 단계 — 완료까지 오랜 기간 소요 예상',
      '소규모 특성상 시공사 유치 어려울 수 있음',
    ],
    risks: [
      '소규모 단지 재건축 사업성 검토 결과에 따라 진행 여부 불투명',
      '인근 대단지(헬리오시티 등)와의 시세 경쟁 제한적',
    ],
    wifePersuasionPoints: [
      '진입 부담이 낮아 무리하지 않는 갈아타기 가능',
      '헬리오시티 바로 옆 생활 인프라 활용 가능',
      '8호선으로 강남 직통 접근',
    ],
    recommendationRank: 5,
    recommendationSummary: '예산 내 진입 용이. 사업시행인가 완료. 소규모 리스크 감안 시 중간 순위',
  },

  // ─── 4. 가락극동아파트 ──────────────────────────────────────────
  {
    id: 'garak-dongbang',
    name: '가락극동아파트',
    shortName: '가락극동',
    type: 'target',

    location: {
      address: '서울 송파구 가락동',
      district: '송파구',
      neighborhood: '가락동',
      lat: 37.4993,
      lng: 127.1220,
      subwayStations: [
        { name: '가락시장역', line: '8호선', walkMinutes: 6 },
        { name: '송파역', line: '8호선', walkMinutes: 7 },
      ],
      nearbySchools: [
        { name: '가락초등학교', type: '초', distanceM: 450 },
        { name: '가락중학교', type: '중', distanceM: 580 },
      ],
      nearbyFeatures: [
        '가락시장 인근',
        '헬리오시티 인근',
        '문정 업무지구',
      ],
    },

    basicInfo: {
      builtYear: 1985,
      totalUnits: 555,
      floorAreaRatio: 195,
      buildingCoverage: 24,
      avgLandShare: 16,
      verified: false,
    },

    prices: {
      current24py: 99000,
      current32py: 125000,
      current34py: 132000,
      current42py: 188000,
      recentTransactionDate: '2025-09',
      highestPrice24py: 135000,
      highestPrice32py: 170000,
      highestPriceDate: '2022-01',
      recoveryRate: 74,
      priceHistory: [
        { date: '2020-01', price24py: 56000, price32py: 71000 },
        { date: '2020-07', price24py: 68000, price32py: 86000 },
        { date: '2021-01', price24py: 90000, price32py: 113000 },
        { date: '2021-07', price24py: 120000, price32py: 152000 },
        { date: '2022-01', price24py: 135000, price32py: 170000 },
        { date: '2022-07', price24py: 118000, price32py: 148000 },
        { date: '2023-01', price24py: 95000, price32py: 120000 },
        { date: '2023-07', price24py: 96000, price32py: 121000 },
        { date: '2024-01', price24py: 96000, price32py: 121000 },
        { date: '2024-07', price24py: 97000, price32py: 122000 },
        { date: '2025-01', price24py: 98000, price32py: 123000 },
        { date: '2025-09', price24py: 99000, price32py: 125000 },
      ],
      verified: false,
      dataSource: '웹서치 기반 (149㎡ 2025.09 실거래 18.8억, 평당 약 4,143만원으로 역산). 30평 기준 추정. 국토부 실거래가 재확인 권장',
    },

    reconstruction: {
      stage: '사업시행인가',
      stageCode: 5,
      stageDetail: '2025년 3월 사업시행계획 인가 완료 (가락미륭·극동·프라자 통합). 기존 555세대 → 지하3층~지상35층 945~975세대 예정. 주력 평형 42평·51평·24평·30평',
      associationEstablished: true,
      businessApprovalDate: '2025-03',
      managementDisposalDate: '',
      relocationCompleted: false,
      constructionStarted: false,
      expectedCompletion: '2031년 이후 (확인 필요)',
      expectedUnitsAfter: 960,
      expectedFARAfter: 300,
      generalSaleUnits: 300,
      contractor: '미정',
      expectedBrand: '미정',
      profitabilityNotes: '555세대 → 960세대 재건축. 가락미륭·프라자 통합으로 대규모 사업. 2025.03 사업시행인가로 속도 빨라짐',
      verified: false,
      dataSource: '뉴스 기반 (2025.03 사업시행인가 확인, 정비사업 정보몽땅 재확인 권장)',
    },

    scores: {
      location: 80,
      school: 74,
      transport: 83,
      profitability: 68,
      risk: 54,
      overall: 72,
      investmentAttractiveness: 70,
      livingComfort: 72,
    },

    pros: [
      '8호선 가락시장역 도보 6분',
      '헬리오시티 인근 생활 인프라',
      '상대적으로 낮은 진입가 — 예산 내 가능',
      '문정 법조타운 업무지구 접근성',
    ],
    cons: [
      '336세대 중소 규모 — 단독 재건축 시 사업성 제한',
      '재건축 단계가 초기 — 불확실성 높음',
      '가락미륭·프라자와 통합 재건축 논의 필요할 수 있음',
    ],
    risks: [
      '소규모 단지 재건축 사업성 불확실',
      '인근 단지와의 통합 재건축 논의 장기화 가능성',
    ],
    wifePersuasionPoints: [
      '헬리오시티 옆 생활권 — 백화점·마트·병원 모두 도보 거리',
      '8호선 직통으로 강남 출퇴근 편리',
    ],
    recommendationRank: 4,
    recommendationSummary: '가락동 내 교통 접근성 우수. 사업시행인가 완료. 30평형 기준 예산 내 진입 가능',
  },

  // ─── 5. 과천 래미안슈르 ─────────────────────────────────────────
  {
    id: 'gwacheon-raemian-shure',
    name: '과천래미안슈르',
    shortName: '과천래미안슈르',
    type: 'target',

    location: {
      address: '경기도 과천시 별양동·원문동',
      district: '과천시',
      neighborhood: '별양동',
      lat: 37.4320,
      lng: 127.0025,
      subwayStations: [
        { name: '과천역', line: '4호선', walkMinutes: 10 },
        { name: '정부청사역', line: '4호선', walkMinutes: 12 },
      ],
      nearbySchools: [
        { name: '별양초등학교', type: '초', distanceM: 400 },
        { name: '과천중학교', type: '중', distanceM: 600 },
        { name: '과천고등학교', type: '고', distanceM: 700 },
      ],
      nearbyFeatures: [
        '4호선 과천역·정부청사역 역세권',
        '과천 정부청사 인근',
        '과천대공원·서울대공원 인접',
        '과천과학관',
        '관악산 등산로',
        '경마공원 인근',
      ],
    },

    basicInfo: {
      builtYear: 2006,
      totalUnits: 3143,
      floorAreaRatio: 195,
      buildingCoverage: 20,
      avgLandShare: 13,
      verified: false,
    },

    prices: {
      current24py: 163000,
      current32py: 205000,
      current34py: 218000,
      current42py: 275000,
      recentTransactionDate: '2026-04',
      highestPrice24py: 183000,
      highestPrice32py: 230000,
      highestPriceDate: '2022-01',
      recoveryRate: 89,
      priceHistory: [
        { date: '2020-01', price24py: 64000, price32py: 80000 },
        { date: '2020-07', price24py: 80000, price32py: 100000 },
        { date: '2021-01', price24py: 112000, price32py: 140000 },
        { date: '2021-07', price24py: 152000, price32py: 190000 },
        { date: '2022-01', price24py: 183000, price32py: 230000 },
        { date: '2022-07', price24py: 156000, price32py: 195000 },
        { date: '2023-01', price24py: 120000, price32py: 150000 },
        { date: '2023-07', price24py: 118000, price32py: 148000 },
        { date: '2024-01', price24py: 111000, price32py: 139000 },
        { date: '2024-07', price24py: 128000, price32py: 160000 },
        { date: '2025-04', price24py: 140000, price32py: 175000 },
        { date: '2025-08', price24py: 163000, price32py: 204000 },
        { date: '2026-04', price24py: 163000, price32py: 205000 },
      ],
      verified: false,
      dataSource: '실거래 기반 (2024.01=13.9억, 2025.04=17.5억, 2025.08=20.4억, 2026.04=20.5억 확인). 국토부 실거래가 공개시스템 재확인 권장',
    },

    reconstruction: {
      stage: '재건축 가능 검토 단계',
      stageCode: 1,
      stageDetail: '용적률 195%로 재건축 요건 충족 가능 — 공식 추진 미확인, 초기 검토 단계',
      associationEstablished: false,
      businessApprovalDate: '',
      managementDisposalDate: '',
      relocationCompleted: false,
      constructionStarted: false,
      expectedCompletion: '미정 (재건축 미추진)',
      expectedUnitsAfter: 4500,
      expectedFARAfter: 270,
      generalSaleUnits: 1200,
      contractor: '미정',
      expectedBrand: '미정 (대형 브랜드 가능성)',
      profitabilityNotes: '용적률 195% → 재건축 법적 요건 충족 가능. 3,143세대 대단지 — 재건축 시 사업성 우수 예상. 단, 2006년 준공으로 재건축 추진 시기는 상당히 장기적',
      verified: false,
      dataSource: '확인 필요 (과천시청 공식 자료 재확인 권장)',
    },

    scores: {
      location: 72,
      school: 75,
      transport: 70,
      profitability: 75,
      risk: 60,
      overall: 72,
      investmentAttractiveness: 73,
      livingComfort: 78,
    },

    pros: [
      '용적률 195% — 재건축 법적 요건 충족 가능 (200% 미만)',
      '3,143세대 대단지 — 재건축 시 사업성 우수 예상',
      '4호선 역세권 (과천역·정부청사역 인근)',
      '과천대공원·서울대공원·관악산 등 자연환경 탁월',
      '5개 송파구 단지 대비 현재 매수가 낮아 진입 유리',
      '과천 정부청사 인근 — 안정적 수요 기반',
    ],
    cons: [
      '서울이 아닌 경기도 과천 — 서울 프리미엄 미적용',
      '2006년 준공 — 재건축 추진까지 장기간 소요',
      '현재 재건축 공식 추진 없음 — 불확실성 최고 수준',
      '서울 도심 접근에 4호선 환승 필요 (30~40분)',
    ],
    risks: [
      '재건축 미추진 시 단순 노후 아파트로 전락 가능',
      '경기도 소재로 정책 변화(투기과열구역 지정 등) 영향 다를 수 있음',
      '재건축 추진 자체가 장기 미정 — 투자 시간가치 리스크',
    ],
    wifePersuasionPoints: [
      '과천대공원·서울대공원 도보권 — 아이와 주말 나들이 최고 환경',
      '관악산 등산로 인접 — 자연 속 생활',
      '3,143세대 대단지 — 단지 내 모든 편의시설 완비',
      '과천 학군 준수 — 안정적인 교육 환경',
    ],
    recommendationRank: 6,
    recommendationSummary: '서울 외 과천 입지지만 용적률 195%로 재건축 잠재력 보유. 자연환경·대단지 강점. 재건축 불확실성 높아 장기 투자 관점 필요',
  },

  // ─── 6. 가락프라자아파트 ────────────────────────────────────────
  {
    id: 'garak-plaza',
    name: '가락프라자아파트',
    shortName: '가락프라자',
    type: 'target',

    location: {
      address: '서울 송파구 가락동',
      district: '송파구',
      neighborhood: '가락동',
      lat: 37.5000,
      lng: 127.1213,
      subwayStations: [
        { name: '송파역', line: '8호선', walkMinutes: 5 },
        { name: '가락시장역', line: '8호선', walkMinutes: 8 },
      ],
      nearbySchools: [
        { name: '가락초등학교', type: '초', distanceM: 380 },
        { name: '거원중학교', type: '중', distanceM: 450 },
      ],
      nearbyFeatures: [
        '헬리오시티 직접 인접',
        '가락시장 인근',
        '성내천 인근',
      ],
    },

    basicInfo: {
      builtYear: 1985,
      totalUnits: 672,
      floorAreaRatio: 196,
      buildingCoverage: 24,
      avgLandShare: 17,
      verified: false,
    },

    prices: {
      current24py: 110000,
      current32py: 138000,
      current34py: 145000,
      current42py: 185000,
      recentTransactionDate: '2025-04',
      highestPrice24py: 150000,
      highestPrice32py: 186000,
      highestPriceDate: '2022-01',
      recoveryRate: 74,
      priceHistory: [
        { date: '2020-01', price24py: 64000, price32py: 80000 },
        { date: '2020-07', price24py: 78000, price32py: 97000 },
        { date: '2021-01', price24py: 102000, price32py: 128000 },
        { date: '2021-07', price24py: 132000, price32py: 165000 },
        { date: '2022-01', price24py: 150000, price32py: 186000 },
        { date: '2022-07', price24py: 136000, price32py: 170000 },
        { date: '2023-01', price24py: 108000, price32py: 135000 },
        { date: '2023-07', price24py: 108000, price32py: 135000 },
        { date: '2024-01', price24py: 108000, price32py: 135000 },
        { date: '2024-07', price24py: 109000, price32py: 136000 },
        { date: '2025-01', price24py: 110000, price32py: 137000 },
        { date: '2025-04', price24py: 110000, price32py: 138000 },
      ],
      verified: false,
      dataSource: '웹서치 기반 추정 (가락동 재건축 단지 비교). 국토부 실거래가 공개시스템 재확인 필수',
    },

    reconstruction: {
      stage: '사업시행인가',
      stageCode: 5,
      stageDetail: '2025년 3월 사업시행계획 인가 완료 (가락미륭·극동·프라자 통합). 기존 672세대 → 최고 34층 11개동 1,059세대(공공임대 106 포함) 예정. 2027년 하반기 착공 목표',
      associationEstablished: true,
      businessApprovalDate: '2025-03',
      managementDisposalDate: '',
      relocationCompleted: false,
      constructionStarted: false,
      expectedCompletion: '2030년 이후 (확인 필요)',
      expectedUnitsAfter: 1059,
      expectedFARAfter: 300,
      generalSaleUnits: 300,
      contractor: '미정',
      expectedBrand: '미정',
      profitabilityNotes: '672세대 → 1,059세대. 가락미륭·극동과 통합 재건축으로 규모 확대. 2025.03 사업시행인가로 사업 속도 빨라짐',
      verified: false,
      dataSource: '뉴스 기반 (하우징헤럴드 통합심의 통과, 2025.03 사업시행인가 확인)',
    },

    scores: {
      location: 79,
      school: 74,
      transport: 82,
      profitability: 65,
      risk: 58,
      overall: 70,
      investmentAttractiveness: 68,
      livingComfort: 73,
    },

    pros: [
      '8호선 송파역 도보 5분 — 역세권 입지',
      '헬리오시티 직접 인접 — 생활 편의시설 최상',
      '대지지분 17평 — 사업성 긍정적',
      '진입가 낮아 예산 여유 확보 가능',
    ],
    cons: [
      '264세대 최소 규모 — 재건축 단독 추진 시 사업성 불확실',
      '재건축 가장 초기 단계 — 불확실성 최고',
      '소규모 특성상 브랜드 아파트 시공사 유치 어려울 수 있음',
    ],
    risks: [
      '소규모 단지 재건축 미추진 가능성',
      '인근 단지와의 통합 재건축 협의가 장기화될 경우 투자 시간가치 손실',
    ],
    wifePersuasionPoints: [
      '헬리오시티 바로 옆 — 대단지 인프라를 이미 누릴 수 있음',
      '8호선 송파역 5분 — 강남까지 직통',
      '예산 내에서 여유롭게 진입 가능한 유일한 선택지',
    ],
    recommendationRank: 7,
    recommendationSummary: '사업시행인가 완료(2025.03). 672세대→1,059세대 통합 재건축. 단, 예산 초과 없는지 확인 필요',
  },
];

export const getComplexById = (id: string): Complex | undefined =>
  COMPLEXES.find((c) => c.id === id);

// 비교 기준 평형: 현재 아파트 24평, 타겟 아파트 comparePy평 (기본 32평)
export function getComparisonPrice(complex: Complex): number {
  if (complex.type === 'target') {
    if (complex.comparePy === 27 && complex.prices.current27py) return complex.prices.current27py;
    if (complex.prices.current32py) return complex.prices.current32py;
  }
  return complex.prices.current24py;
}

export function getComparisonSize(complex: Complex): string {
  if (complex.type !== 'target') return '24평';
  return complex.comparePy ? `${complex.comparePy}평` : '32평';
}

export function getComparisonHighestPrice(complex: Complex): number {
  if (complex.type === 'target') {
    if (complex.comparePy === 27 && complex.prices.highestPrice27py) return complex.prices.highestPrice27py;
    if (complex.prices.highestPrice32py) return complex.prices.highestPrice32py;
  }
  return complex.prices.highestPrice24py;
}

export function getComparisonPriceKey(complex: Complex): 'price24py' | 'price27py' | 'price32py' {
  if (complex.type !== 'target') return 'price24py';
  if (complex.comparePy === 27) return 'price27py';
  return 'price32py';
}

export const TARGET_COMPLEXES = COMPLEXES.filter((c) => c.type === 'target');

export const CURRENT_APARTMENT = COMPLEXES.find((c) => c.type === 'current')!;

export const STAGE_LABELS: Record<number, { label: string; color: string }> = {
  0: { label: '해당없음', color: 'gray' },
  1: { label: '기본계획', color: 'gray' },
  2: { label: '정비구역 지정', color: 'yellow' },
  3: { label: '조합설립 추진', color: 'yellow' },
  4: { label: '조합설립인가', color: 'blue' },
  5: { label: '사업시행인가', color: 'blue' },
  6: { label: '관리처분인가', color: 'indigo' },
  7: { label: '이주/철거', color: 'purple' },
  8: { label: '착공', color: 'green' },
  9: { label: '준공', color: 'green' },
};
