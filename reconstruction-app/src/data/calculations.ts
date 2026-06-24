import { FeasibilityResult, SimulationParams } from './types';
import { Complex } from './types';

// 취득세 계산 (1세대 1주택 기준, 조정대상지역 외)
export function calcAcquisitionTax(priceWon: number): number {
  if (priceWon <= 600_000_000) return priceWon * 0.01;
  if (priceWon <= 900_000_000) {
    const rate = ((priceWon * 2 - 600_000_000) / 900_000_000 * 2 + 1) / 100;
    return priceWon * rate;
  }
  return priceWon * 0.03;
}

// 중개수수료 (상한 요율 기준, 협의 가능)
export function calcAgencyFee(priceWon: number): number {
  if (priceWon < 200_000_000) return priceWon * 0.005;
  if (priceWon < 900_000_000) return priceWon * 0.004;
  return priceWon * 0.007;
}

// 이사비 + 예비비
export const MOVING_COST = 3_000_000;  // 이사비 300만원
export const CONTINGENCY = 5_000_000;  // 예비비 500만원

// 만원 → 원
export const toWon = (manwon: number) => manwon * 10_000;

// 원 → 만원
export const toManwon = (won: number) => Math.round(won / 10_000);

// 억원 포맷
export function formatPrice(manwon: number): string {
  if (manwon >= 10000) {
    const eok = Math.floor(manwon / 10000);
    const rest = manwon % 10000;
    if (rest === 0) return `${eok}억`;
    return `${eok}억 ${rest.toLocaleString()}만원`;
  }
  return `${manwon.toLocaleString()}만원`;
}

// 억 단위 (소수점 1자리)
export function formatEok(manwon: number): string {
  return `${(manwon / 10000).toFixed(1)}억`;
}

// 자금 실행 가능성 판단
export function calcFeasibility(
  complex: Complex,
  params: SimulationParams
): FeasibilityResult {
  const priceManwon = complex.type === 'target' && complex.prices.current32py
    ? complex.prices.current32py
    : complex.prices.current24py;
  const priceWon = toWon(priceManwon);
  const sellPriceWon = toWon(params.sellPrice);
  const cashWon = toWon(params.cash);
  const loanWon = toWon(params.loan);

  const acquisitionTax = calcAcquisitionTax(priceWon);
  const agencyFee = calcAgencyFee(priceWon) + calcAgencyFee(sellPriceWon); // 매수+매도
  const movingCost = MOVING_COST;
  const contingency = CONTINGENCY;

  const totalCost = priceWon + acquisitionTax + agencyFee + movingCost + contingency;
  const available = sellPriceWon + cashWon + loanWon;
  const shortfall = Math.max(0, totalCost - available);

  let status: FeasibilityResult['status'];
  const requiredLoan = Math.max(0, totalCost - sellPriceWon - cashWon);
  const requiredLoanManwon = toManwon(requiredLoan);

  if (shortfall > 0) {
    status = '불가';
  } else if (requiredLoanManwon > 50000) {
    status = '무리';
  } else if (requiredLoanManwon > 30000) {
    status = '주의';
  } else {
    status = '가능';
  }

  return {
    complexId: complex.id,
    targetPrice: priceManwon,
    acquisitionTax: toManwon(acquisitionTax),
    agencyFee: toManwon(agencyFee),
    movingCost: toManwon(movingCost),
    contingency: toManwon(contingency),
    totalCost: toManwon(totalCost),
    totalRequired: toManwon(totalCost),
    available: toManwon(available),
    shortfall: toManwon(shortfall),
    status,
  };
}

// 인덕원 보유 시 기회비용 계산 (연 % 대비)
export function calcOpportunityCost(
  indukwonPrice: number,
  targetPrice: number,
  years: number,
  targetGrowthRate: number,
  indukwonGrowthRate: number
): { indukwonFinal: number; targetFinal: number; difference: number } {
  const indukwonFinal = indukwonPrice * Math.pow(1 + indukwonGrowthRate / 100, years);
  const targetFinal = targetPrice * Math.pow(1 + targetGrowthRate / 100, years);
  return {
    indukwonFinal: Math.round(indukwonFinal),
    targetFinal: Math.round(targetFinal),
    difference: Math.round(targetFinal - indukwonFinal),
  };
}

// 재건축 후 예상 시세 계산
export function calcExpectedPriceAfterReconstruction(
  complex: Complex,
  nearbyNewPrice: number
): number {
  return Math.round(nearbyNewPrice * 1.1); // 재건축 후 인근 신축 대비 10% 프리미엄 가정
}

// 투자 매력도 종합 점수
export function calcOverallScore(complex: Complex): number {
  const { location, school, transport, profitability, risk } = complex.scores;
  return Math.round(
    location * 0.25 +
    school * 0.15 +
    transport * 0.2 +
    profitability * 0.25 +
    (100 - risk) * 0.15
  );
}

// 재건축 사업 단계 진행률 (%)
export function calcStageProgress(stageCode: number): number {
  return Math.round((stageCode / 9) * 100);
}

export const DEFAULT_SIMULATION: SimulationParams = {
  sellPrice: 120000,
  cash: 50000,
  loan: 30000,
  ltv: 40,
  dsr: 40,
};
