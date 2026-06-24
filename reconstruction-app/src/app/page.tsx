import Link from 'next/link';
import { TARGET_COMPLEXES, CURRENT_APARTMENT } from '@/data/complexes';
import { formatPrice, calcFeasibility, DEFAULT_SIMULATION } from '@/data/calculations';
import StageBadge from '@/components/StageBadge';
import FeasibilityBadge from '@/components/FeasibilityBadge';
import ScoreBar from '@/components/ScoreBar';

const RANK_COLORS = ['', 'bg-yellow-500', 'bg-gray-400', 'bg-amber-700', 'bg-slate-400', 'bg-slate-300'];
const RANK_LABELS = ['', '1순위', '2순위', '3순위', '4순위', '5순위'];

export default function DashboardPage() {
  const myAssets = {
    sellPrice: DEFAULT_SIMULATION.sellPrice,
    cash: DEFAULT_SIMULATION.cash,
    total: DEFAULT_SIMULATION.sellPrice + DEFAULT_SIMULATION.cash,
  };

  const feasibilities = TARGET_COMPLEXES.map((c) =>
    calcFeasibility(c, DEFAULT_SIMULATION)
  );

  const sorted = [...TARGET_COMPLEXES].sort(
    (a, b) => a.recommendationRank - b.recommendationRank
  );

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-8">

      {/* Hero */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-2xl p-6 text-white">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <p className="text-blue-200 text-sm font-medium mb-1">의사결정 보조 도구</p>
            <h1 className="text-2xl sm:text-3xl font-black">
              인덕원 → 송파 재건축 갈아타기 분석기
            </h1>
            <p className="text-blue-100 mt-2 text-sm">
              인덕원마을삼성 24평 매도 후 송파구 재건축 단지 진입 시나리오
            </p>
          </div>
          <div className="flex gap-3 flex-wrap">
            <div className="bg-white/15 rounded-xl p-3 min-w-[100px] text-center">
              <p className="text-xs text-blue-200">현재 아파트 시세</p>
              <p className="text-xl font-black">{formatPrice(CURRENT_APARTMENT.prices.current24py)}</p>
            </div>
            <div className="bg-white/15 rounded-xl p-3 min-w-[100px] text-center">
              <p className="text-xs text-blue-200">보유 현금</p>
              <p className="text-xl font-black">{formatPrice(myAssets.cash)}</p>
            </div>
            <div className="bg-white/25 rounded-xl p-3 min-w-[110px] text-center border border-white/30">
              <p className="text-xs text-blue-200">총 자기자본</p>
              <p className="text-xl font-black">{formatPrice(myAssets.total)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick nav */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { href: '/map', label: '지도로 보기', icon: '🗺️', desc: '입지 비교' },
          { href: '/compare', label: '비교 테이블', icon: '📋', desc: '전항목 비교' },
          { href: '/simulation', label: '자금 시뮬레이션', icon: '💰', desc: '예산 계산' },
          { href: '/summary', label: '아내 설득 요약', icon: '💡', desc: '핵심 논리' },
        ].map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 hover:shadow-md hover:border-blue-200 transition-all text-center group"
          >
            <div className="text-2xl mb-1">{item.icon}</div>
            <div className="font-bold text-gray-800 text-sm group-hover:text-blue-700">{item.label}</div>
            <div className="text-xs text-gray-400 mt-0.5">{item.desc}</div>
          </Link>
        ))}
      </div>

      {/* Data warning */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-3 flex gap-2 items-start">
        <span className="text-yellow-600 text-lg flex-shrink-0">⚠️</span>
        <p className="text-xs text-yellow-700">
          <strong>모의 데이터 안내:</strong> 모든 가격·사업 단계 정보는 실제 재확인이 필요한 추정치입니다.
          실제 투자 결정 전 반드시 <strong>국토부 실거래가 공개시스템</strong> 및 <strong>서울시 정비사업 정보몽땅</strong>에서 최신 정보를 확인하세요.
        </p>
      </div>

      {/* Top 3 Recommendation */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-black text-gray-900">추천 순위 TOP 3</h2>
          <Link href="/compare" className="text-sm text-blue-600 hover:underline">전체 비교 →</Link>
        </div>
        <div className="grid sm:grid-cols-3 gap-4">
          {sorted.slice(0, 3).map((complex) => {
            const f = feasibilities.find((f) => f.complexId === complex.id)!;
            return (
              <Link
                key={complex.id}
                href={`/complex/${complex.id}`}
                className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-lg hover:border-blue-200 transition-all group"
              >
                <div className="flex items-start justify-between mb-3">
                  <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-white text-sm font-black ${RANK_COLORS[complex.recommendationRank]}`}>
                    {complex.recommendationRank}
                  </span>
                  <FeasibilityBadge status={f.status} />
                </div>
                <h3 className="font-black text-gray-900 text-base group-hover:text-blue-700 mb-1">
                  {complex.shortName}
                </h3>
                <p className="text-xs text-gray-500 mb-3">{complex.location.neighborhood}</p>

                <div className="flex justify-between items-end mb-4">
                  <div>
                    <p className="text-xs text-gray-400">24평 현재가 (추정)</p>
                    <p className="text-lg font-black text-gray-900">{formatPrice(complex.prices.current24py)}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-400">전고점 회복률</p>
                    <p className={`text-sm font-bold ${complex.prices.recoveryRate >= 90 ? 'text-green-600' : complex.prices.recoveryRate >= 80 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {complex.prices.recoveryRate}%
                    </p>
                  </div>
                </div>

                <StageBadge stageCode={complex.reconstruction.stageCode} />

                <div className="mt-3 space-y-1.5">
                  <ScoreBar label="종합 점수" score={complex.scores.overall} />
                  <ScoreBar label="입지" score={complex.scores.location} />
                </div>

                <p className="text-xs text-gray-500 mt-3 line-clamp-2">{complex.recommendationSummary}</p>
              </Link>
            );
          })}
        </div>
      </div>

      {/* All complexes grid */}
      <div>
        <h2 className="text-xl font-black text-gray-900 mb-4">전체 비교 단지 ({TARGET_COMPLEXES.length}개)</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {TARGET_COMPLEXES.map((complex) => {
            const f = feasibilities.find((f) => f.complexId === complex.id)!;
            return (
              <Link
                key={complex.id}
                href={`/complex/${complex.id}`}
                className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 hover:shadow-md hover:border-blue-200 transition-all group"
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-bold text-gray-900 group-hover:text-blue-700">{complex.shortName}</h3>
                  <span className={`text-xs font-bold px-2 py-0.5 rounded-full text-white ${RANK_COLORS[complex.recommendationRank]}`}>
                    {RANK_LABELS[complex.recommendationRank]}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-2 mb-3 text-center">
                  <div>
                    <p className="text-xs text-gray-400">현재가(추정)</p>
                    <p className="text-sm font-black text-gray-900">{formatPrice(complex.prices.current24py)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">세대수</p>
                    <p className="text-sm font-bold text-gray-700">{complex.basicInfo.totalUnits.toLocaleString()}세대</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">회복률</p>
                    <p className="text-sm font-bold text-gray-700">{complex.prices.recoveryRate}%</p>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <StageBadge stageCode={complex.reconstruction.stageCode} />
                  <FeasibilityBadge status={f.status} />
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Current vs Target quick compare */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-xl font-black text-gray-900 mb-4">인덕원 vs 송파 핵심 비교</h2>
        <div className="overflow-x-auto scrollbar-hide">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="text-left py-2 pr-4 text-gray-500 font-medium">항목</th>
                <th className="text-center py-2 px-3 text-gray-700 font-bold whitespace-nowrap">인덕원삼성</th>
                {sorted.slice(0, 3).map((c) => (
                  <th key={c.id} className="text-center py-2 px-3 text-blue-700 font-bold whitespace-nowrap">
                    {c.shortName}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[
                {
                  label: '현재 시세 (24평)',
                  current: formatPrice(CURRENT_APARTMENT.prices.current24py),
                  values: sorted.slice(0, 3).map((c) => formatPrice(c.prices.current24py)),
                },
                {
                  label: '소재지',
                  current: CURRENT_APARTMENT.location.district,
                  values: sorted.slice(0, 3).map((c) => c.location.district),
                },
                {
                  label: '준공연도',
                  current: `${CURRENT_APARTMENT.basicInfo.builtYear}년`,
                  values: sorted.slice(0, 3).map((c) => `${c.basicInfo.builtYear}년`),
                },
                {
                  label: '세대수',
                  current: `${CURRENT_APARTMENT.basicInfo.totalUnits.toLocaleString()}세대`,
                  values: sorted.slice(0, 3).map((c) => `${c.basicInfo.totalUnits.toLocaleString()}세대`),
                },
                {
                  label: '사업 단계',
                  current: CURRENT_APARTMENT.reconstruction.stage,
                  values: sorted.slice(0, 3).map((c) => c.reconstruction.stage),
                },
                {
                  label: '예상 완공',
                  current: CURRENT_APARTMENT.reconstruction.expectedCompletion,
                  values: sorted.slice(0, 3).map((c) => c.reconstruction.expectedCompletion),
                },
                {
                  label: '종합 점수',
                  current: `${CURRENT_APARTMENT.scores.overall}점`,
                  values: sorted.slice(0, 3).map((c) => `${c.scores.overall}점`),
                },
              ].map((row) => (
                <tr key={row.label} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="py-2.5 pr-4 text-gray-500 whitespace-nowrap">{row.label}</td>
                  <td className="py-2.5 px-3 text-center text-gray-700">{row.current}</td>
                  {row.values.map((v, i) => (
                    <td key={i} className="py-2.5 px-3 text-center font-medium text-blue-700">{v}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-gray-400 mt-3">* 모든 가격은 추정치. 실거래가 공개시스템 재확인 필요</p>
      </div>

    </div>
  );
}
