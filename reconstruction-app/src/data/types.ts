export interface PricePoint {
  date: string; // YYYY-MM
  price24py: number; // 만원
  price34py?: number;
  price42py?: number;
}

export interface SubwayStation {
  name: string;
  line: string;
  walkMinutes: number;
}

export interface NearbySchool {
  name: string;
  type: '초' | '중' | '고';
  distanceM: number;
  reputation?: string;
}

export type StageCode = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9;

export interface Complex {
  id: string;
  name: string;
  shortName: string;
  type: 'target' | 'current';

  location: {
    address: string;
    district: string;
    neighborhood: string;
    lat: number;
    lng: number;
    subwayStations: SubwayStation[];
    nearbySchools: NearbySchool[];
    nearbyFeatures: string[];
  };

  basicInfo: {
    builtYear: number;
    totalUnits: number;
    floorAreaRatio: number;
    buildingCoverage: number;
    avgLandShare: number;
    verified: boolean;
  };

  prices: {
    current24py: number;
    current34py: number;
    current42py: number;
    recentTransactionDate: string;
    highestPrice24py: number;
    highestPriceDate: string;
    recoveryRate: number;
    priceHistory: PricePoint[];
    verified: boolean;
    dataSource: string;
  };

  reconstruction: {
    stage: string;
    stageCode: StageCode;
    stageDetail: string;
    associationEstablished: boolean;
    businessApprovalDate: string;
    managementDisposalDate: string;
    relocationCompleted: boolean;
    constructionStarted: boolean;
    expectedCompletion: string;
    expectedUnitsAfter: number;
    expectedFARAfter: number;
    generalSaleUnits: number;
    contractor: string;
    expectedBrand: string;
    profitabilityNotes: string;
    verified: boolean;
    dataSource: string;
  };

  scores: {
    location: number;
    school: number;
    transport: number;
    profitability: number;
    risk: number;
    overall: number;
    investmentAttractiveness: number;
    livingComfort: number;
  };

  pros: string[];
  cons: string[];
  risks: string[];
  wifePersuasionPoints: string[];
  recommendationRank: number;
  recommendationSummary: string;
}

export interface MyAssets {
  currentApartmentName: string;
  currentApartmentArea: number;
  sellPrice: number;
  cash: number;
  total: number;
}

export interface SimulationParams {
  sellPrice: number;
  cash: number;
  loan: number;
  ltv: number;
  dsr: number;
}

export interface FeasibilityResult {
  complexId: string;
  targetPrice: number;
  acquisitionTax: number;
  agencyFee: number;
  movingCost: number;
  contingency: number;
  totalCost: number;
  totalRequired: number;
  available: number;
  shortfall: number;
  status: '가능' | '주의' | '무리' | '불가';
}
