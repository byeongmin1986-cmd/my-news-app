'use client';
import { useState } from 'react';
import { TARGET_COMPLEXES } from '@/data/complexes';
import { formatPrice, calcFeasibility, toWon, calcAcquisitionTax, calcAgencyFee, MOVING_COST, CONTINGENCY, toManwon } from '@/data/calculations';
import FeasibilityBadge from '@/components/FeasibilityBadge';
import Link from 'next/link';

const SELL_OPTIONS = [115000, 120000, 125000] as const;
const LOAN_OPTIONS = [0, 20000, 30000, 40000, 50000] as const;

export default function SimulationPage() {
  const [sellPrice, setSellPrice] = useState<number>(120000);
  const [cash] = useState<number>(50000);
  const [loan, setLoan] = useState<number>(30000);
  const [ltv, setLtv] = useState<number>(40);
  const [dsr, setDsr] = useState<number>(40);
  const [selectedComplex, setSelectedComplex] = useState<string | null>(null);

  const total = sellPrice + cash + loan;

  const results = TARGET_COMPLEXES.map((complex) => {
    const f = calcFeasibility(complex, { sellPrice, cash, loan, ltv, dsr });
    return { complex, f };
  });

  const selected = selectedComplex
    ? results.find((r) => r.complex.id === selectedComplex)
    : null;

  // 취득세 계산 (선택된 단지 또는 첫 번째)
  const sampleComplex = selected?.complex ?? TARGET_COMPLEXES[0];
  const samplePrice = toWon(sampleComplex.prices.current24py);
  const acqTax = toManwon(calcAcquisitionTax(samplePrice));
  const agFee = toManwon(calcAgencyFee(samplePrice) + calcAgencyFee(toWon(sellPrice)));
  const misc = toManwon(MOVING_COST + CONTINGENCY);
  const totalExtra = acqTax + agFee + misc;

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 space-y-6">
      <div>
        <h1 className="text-2xl font-black text-gray-900">자금 시뮬레이션</h1>
        <p className="text-gray-500 text-sm mt-1">매도가·대출 조건을 바꾸면 단지별 자금 여건이 실시간으로 업데이트됩니다.</p>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-3 text-xs text-yellow-700">
        ⚠️ 모의 계산입니다. 실제 취득세·중개수수료는 거래 시점과 조건에 따라 달라집니다. 세무사·공인중개사 상담 필수.
      </div>

      {/* Input controls */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">

        {/* 매도가 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
          <h3 className="font-bold text-gray-700 mb-3 text-sm">인덕원삼성 매도가 (24평)</h3>
          <div className="flex gap-2">
            {SELL_OPTIONS.map((v) => (
              <button
                key={v}
                onClick={() => setSellPrice(v)}
                className={`flex-1 py-2.5 rounded-xl text-sm font-bold transition-colors ${
                  sellPrice === v
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {formatPrice(v)}
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-400 mt-2">인덕원마을삼성 24평 최근 시세 기준 (추정)</p>
        </div>

        {/* 현금 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
          <h3 className="font-bold text-gray-700 mb-3 text-sm">보유 현금</h3>
          <div className="bg-green-50 border border-green-200 rounded-xl p-3 text-center">
            <p className="text-2xl font-black text-green-700">{formatPrice(cash)}</p>
            <p className="text-xs text-green-600 mt-0.5">고정 (현재 보유 현금)</p>
          </div>
        </div>

        {/* 대출 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
          <h3 className="font-bold text-gray-700 mb-3 text-sm">추가 대출 가능액</h3>
          <div className="flex flex-wrap gap-2">
            {LOAN_OPTIONS.map((v) => (
              <button
                key={v}
                onClick={() => setLoan(v)}
                className={`flex-1 min-w-[60px] py-2 rounded-xl text-xs font-bold transition-colors ${
                  loan === v
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {v === 0 ? '없음' : formatPrice(v)}
              </button>
            ))}
          </div>
        </div>

        {/* LTV/DSR */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 sm:col-span-2 lg:col-span-3">
          <h3 className="font-bold text-gray-700 mb-3 text-sm">대출 조건 (직접 수정)</h3>
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-gray-500 block mb-1.5">LTV 한도 (%)</label>
              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min={0}
                  max={80}
                  step={5}
                  value={ltv}
                  onChange={(e) => setLtv(Number(e.target.value))}
                  className="flex-1 accent-blue-600"
                />
                <span className="text-lg font-black text-blue-700 w-12 text-right">{ltv}%</span>
              </div>
              <p className="text-xs text-gray-400 mt-1">조정대상지역 1주택: 통상 40~60%</p>
            </div>
            <div>
              <label className="text-xs text-gray-500 block mb-1.5">DSR 한도 (%)</label>
              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min={0}
                  max={60}
                  step={5}
                  value={dsr}
                  onChange={(e) => setDsr(Number(e.target.value))}
                  className="flex-1 accent-blue-600"
                />
                <span className="text-lg font-black text-blue-700 w-12 text-right">{dsr}%</span>
              </div>
              <p className="text-xs text-gray-400 mt-1">DSR: 총부채원리금상환비율</p>
            </div>
          </div>
        </div>
      </div>

      {/* Total summary */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-2xl p-5 text-white">
        <h3 className="font-bold text-blue-200 mb-3 text-sm">내 총 가용 자금</h3>
        <div className="grid grid-cols-4 gap-3">
          {[
            { label: '매도 예상액', value: formatPrice(sellPrice) },
            { label: '보유 현금', value: formatPrice(cash) },
            { label: '대출', value: loan === 0 ? '없음' : formatPrice(loan) },
            { label: '합계', value: formatPrice(total) },
          ].map((item, i) => (
            <div key={item.label} className={`text-center ${i === 3 ? 'border-l border-white/30' : ''}`}>
              <p className="text-xs text-blue-200">{item.label}</p>
              <p className={`font-black ${i === 3 ? 'text-xl' : 'text-lg'}`}>{item.value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Cost breakdown for selected or all */}
      {selected && (
        <div className="bg-white rounded-2xl shadow-sm border border-blue-200 p-5">
          <div className="flex items-start justify-between mb-4">
            <h3 className="font-black text-gray-900 text-lg">{selected.complex.shortName} 자금 상세</h3>
            <button onClick={() => setSelectedComplex(null)} className="text-gray-400 hover:text-gray-600">✕</button>
          </div>
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="space-y-3">
              <h4 className="text-sm font-bold text-gray-700">비용 내역</h4>
              {[
                { label: '매수가 (24평, 추정)', value: formatPrice(selected.f.targetPrice), isMain: true },
                { label: '취득세 (추정, 1주택 기준)', value: formatPrice(selected.f.acquisitionTax), note: '9억 초과: 3%' },
                { label: '중개수수료 (매수+매도)', value: formatPrice(selected.f.agencyFee), note: '상한 기준' },
                { label: '이사비', value: formatPrice(selected.f.movingCost) },
                { label: '예비비', value: formatPrice(selected.f.contingency) },
                { label: '총 필요 금액', value: formatPrice(selected.f.totalRequired), isTotal: true },
              ].map((row) => (
                <div key={row.label} className={`flex justify-between items-center ${row.isTotal ? 'border-t border-gray-200 pt-3 font-black' : ''}`}>
                  <div>
                    <span className={`text-sm ${row.isMain ? 'font-bold text-gray-900' : 'text-gray-600'}`}>{row.label}</span>
                    {row.note && <p className="text-xs text-gray-400">{row.note}</p>}
                  </div>
                  <span className={`text-sm font-bold ${row.isTotal ? 'text-red-600 text-lg' : row.isMain ? 'text-gray-900' : 'text-orange-600'}`}>
                    {row.value}
                  </span>
                </div>
              ))}
            </div>
            <div className="space-y-3">
              <h4 className="text-sm font-bold text-gray-700">자금 여건 판단</h4>
              <div className="bg-gray-50 rounded-xl p-4 space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">총 필요</span>
                  <span className="font-bold text-red-600">{formatPrice(selected.f.totalRequired)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">가용 자금</span>
                  <span className="font-bold text-green-600">{formatPrice(selected.f.available)}</span>
                </div>
                <div className="border-t border-gray-200 pt-2 flex justify-between">
                  <span className="text-sm text-gray-600">차액</span>
                  <span className={`font-black text-lg ${selected.f.shortfall > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {selected.f.shortfall > 0
                      ? `-${formatPrice(selected.f.shortfall)} 부족`
                      : `+${formatPrice(selected.f.available - selected.f.totalRequired)} 여유`}
                  </span>
                </div>
              </div>
              <div className="flex justify-center">
                <FeasibilityBadge status={selected.f.status} />
              </div>
              <div className="bg-blue-50 rounded-xl p-3 text-xs text-blue-700">
                <p className="font-bold mb-1">판단 기준:</p>
                <p>✅ 가능: 대출 없이 또는 3억 이하 대출로 여유 있게 진입</p>
                <p>⚠️ 주의: 3~5억 대출 필요</p>
                <p>🔶 무리: 5억 초과 대출 필요</p>
                <p>❌ 불가: 최대 자금으로도 부족</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Results grid */}
      <div>
        <h2 className="text-xl font-black text-gray-900 mb-4">단지별 자금 여건</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {results
            .sort((a, b) => a.complex.recommendationRank - b.complex.recommendationRank)
            .map(({ complex, f }) => {
              const surplus = f.available - f.totalRequired;
              const isSelected = selectedComplex === complex.id;
              return (
                <button
                  key={complex.id}
                  onClick={() => setSelectedComplex(isSelected ? null : complex.id)}
                  className={`bg-white rounded-2xl shadow-sm border p-5 text-left hover:shadow-md transition-all ${
                    isSelected ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-100'
                  } ${
                    f.status === '가능' ? 'hover:border-green-300'
                    : f.status === '불가' ? 'hover:border-red-300'
                    : 'hover:border-yellow-300'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="text-xs text-gray-400">{complex.recommendationRank}순위 추천</p>
                      <h3 className="font-black text-gray-900 text-base">{complex.shortName}</h3>
                    </div>
                    <FeasibilityBadge status={f.status} />
                  </div>

                  <div className="grid grid-cols-2 gap-3 mb-3">
                    <div className="bg-gray-50 rounded-lg p-2 text-center">
                      <p className="text-xs text-gray-400">매수가 (추정)</p>
                      <p className="text-sm font-black text-gray-900">{formatPrice(f.targetPrice)}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-2 text-center">
                      <p className="text-xs text-gray-400">총 필요금액</p>
                      <p className="text-sm font-black text-red-600">{formatPrice(f.totalRequired)}</p>
                    </div>
                  </div>

                  <div className={`rounded-lg p-2 text-center mb-2 ${surplus >= 0 ? 'bg-green-50' : 'bg-red-50'}`}>
                    <p className="text-xs text-gray-400">자금 {surplus >= 0 ? '여유' : '부족'}</p>
                    <p className={`text-base font-black ${surplus >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {surplus >= 0 ? `+${formatPrice(surplus)}` : `-${formatPrice(Math.abs(surplus))}`}
                    </p>
                  </div>

                  <div className="grid grid-cols-3 gap-1 text-xs text-center text-gray-500">
                    <div>
                      <p className="text-gray-400">취득세(추정)</p>
                      <p className="font-medium">{formatPrice(f.acquisitionTax)}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">중개료</p>
                      <p className="font-medium">{formatPrice(f.agencyFee)}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">이사+예비</p>
                      <p className="font-medium">{formatPrice(f.movingCost + f.contingency)}</p>
                    </div>
                  </div>

                  <p className="text-xs text-blue-600 text-center mt-2">클릭하여 상세 보기</p>
                </button>
              );
            })}
        </div>
      </div>

      {/* Scenario matrix */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
        <h2 className="text-lg font-black text-gray-900 mb-4">시나리오별 진입 가능 매트릭스</h2>
        <p className="text-xs text-gray-400 mb-3">매도가 × 대출액 조합별 단지 진입 가능 여부</p>
        <div className="overflow-x-auto scrollbar-hide">
          <table className="w-full text-xs min-w-[500px]">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="text-left py-2 px-3 text-gray-500">단지</th>
                {SELL_OPTIONS.map((sp) => (
                  LOAN_OPTIONS.map((lo) => (
                    <th key={`${sp}-${lo}`} className="text-center py-2 px-2 text-gray-500 whitespace-nowrap">
                      {formatPrice(sp)}<br/>+{lo === 0 ? '0' : formatPrice(lo)}대출
                    </th>
                  ))
                ))}
              </tr>
            </thead>
            <tbody>
              {TARGET_COMPLEXES.sort((a, b) => a.recommendationRank - b.recommendationRank).map((complex) => (
                <tr key={complex.id} className="border-b border-gray-50">
                  <td className="py-2 px-3 font-bold text-gray-800">{complex.shortName}</td>
                  {SELL_OPTIONS.map((sp) =>
                    LOAN_OPTIONS.map((lo) => {
                      const f = calcFeasibility(complex, { sellPrice: sp, cash, loan: lo, ltv, dsr });
                      const colors: Record<string, string> = {
                        가능: 'bg-green-100 text-green-700',
                        주의: 'bg-yellow-100 text-yellow-700',
                        무리: 'bg-orange-100 text-orange-700',
                        불가: 'bg-red-100 text-red-600',
                      };
                      return (
                        <td key={`${sp}-${lo}`} className="py-2 px-2 text-center">
                          <span className={`px-1.5 py-0.5 rounded text-xs font-bold ${colors[f.status]}`}>
                            {f.status}
                          </span>
                        </td>
                      );
                    })
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="flex gap-3 mt-3 flex-wrap">
          {[
            { status: '가능', color: 'bg-green-100 text-green-700' },
            { status: '주의', color: 'bg-yellow-100 text-yellow-700' },
            { status: '무리', color: 'bg-orange-100 text-orange-700' },
            { status: '불가', color: 'bg-red-100 text-red-600' },
          ].map(({ status, color }) => (
            <span key={status} className={`text-xs px-2 py-1 rounded font-medium ${color}`}>{status}</span>
          ))}
          <span className="text-xs text-gray-400">현금 {formatPrice(cash)} 고정 기준</span>
        </div>
      </div>

      <div className="flex gap-3">
        <Link href="/compare" className="flex-1 text-center bg-gray-100 text-gray-700 rounded-xl py-3 font-bold hover:bg-gray-200 transition-colors">
          ← 비교 테이블
        </Link>
        <Link href="/summary" className="flex-1 text-center bg-blue-600 text-white rounded-xl py-3 font-bold hover:bg-blue-700 transition-colors">
          아내 설득 요약 →
        </Link>
      </div>
    </div>
  );
}
