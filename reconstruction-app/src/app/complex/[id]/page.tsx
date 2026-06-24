'use client';
import { use } from 'react';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getComplexById } from '@/data/complexes';
import { formatPrice, calcFeasibility, DEFAULT_SIMULATION, calcStageProgress } from '@/data/calculations';
import StageBadge from '@/components/StageBadge';
import ScoreBar from '@/components/ScoreBar';
import FeasibilityBadge from '@/components/FeasibilityBadge';
import PriceChart from '@/components/PriceChart';

const STAGE_STEPS = [
  '기본계획',
  '정비구역 지정',
  '추진위 설립',
  '조합설립인가',
  '사업시행인가',
  '관리처분인가',
  '이주/철거',
  '착공',
  '준공',
];

export default function ComplexDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const complex = getComplexById(id);
  if (!complex) notFound();

  const f = calcFeasibility(complex, DEFAULT_SIMULATION);
  const progress = calcStageProgress(complex.reconstruction.stageCode);

  return (
    <div className="max-w-5xl mx-auto px-4 py-6 space-y-6">

      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <Link href="/" className="hover:text-blue-600">대시보드</Link>
        <span>›</span>
        <span className="text-gray-900 font-medium">{complex.name}</span>
      </div>

      {/* Header */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              {complex.type === 'target' && (
                <span className="bg-blue-600 text-white text-xs font-bold px-2 py-0.5 rounded-full">
                  {complex.recommendationRank}순위 추천
                </span>
              )}
              <StageBadge stageCode={complex.reconstruction.stageCode} />
              {!complex.prices.verified && (
                <span className="bg-yellow-100 text-yellow-700 text-xs px-2 py-0.5 rounded-full border border-yellow-200">
                  가격 확인 필요
                </span>
              )}
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-gray-900">{complex.name}</h1>
            <p className="text-gray-500 mt-1">📍 {complex.location.address}</p>
          </div>
          <div className="flex gap-3 flex-wrap sm:flex-col sm:text-right">
            <div className="bg-blue-50 rounded-xl p-3">
              <p className="text-xs text-blue-500">24평 현재 시세 (추정)</p>
              <p className="text-2xl font-black text-blue-700">{formatPrice(complex.prices.current24py)}</p>
            </div>
            {complex.type === 'target' && <FeasibilityBadge status={f.status} className="self-start sm:self-end" />}
          </div>
        </div>
      </div>

      {/* Key stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: '준공연도', value: `${complex.basicInfo.builtYear}년`, sub: `${2025 - complex.basicInfo.builtYear}년 경과` },
          { label: '세대수', value: `${complex.basicInfo.totalUnits.toLocaleString()}세대`, sub: `→ 재건축 후 ${complex.reconstruction.expectedUnitsAfter.toLocaleString()}세대` },
          { label: '현재 용적률', value: `${complex.basicInfo.floorAreaRatio}%`, sub: `→ 재건축 후 ${complex.reconstruction.expectedFARAfter}%` },
          { label: '대지지분(평균)', value: `약 ${complex.basicInfo.avgLandShare}평`, sub: complex.basicInfo.verified ? '' : '확인 필요' },
        ].map((stat) => (
          <div key={stat.label} className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-center">
            <p className="text-xs text-gray-400 mb-1">{stat.label}</p>
            <p className="text-lg font-black text-gray-900">{stat.value}</p>
            {stat.sub && <p className="text-xs text-gray-400 mt-0.5">{stat.sub}</p>}
          </div>
        ))}
      </div>

      {/* Price chart + recovery */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
          <h2 className="text-lg font-black text-gray-900">가격 추이 (24평 기준)</h2>
          <div className="flex gap-3">
            <div className="text-center">
              <p className="text-xs text-gray-400">최고가</p>
              <p className="text-sm font-bold text-red-600">{formatPrice(complex.prices.highestPrice24py)}</p>
              <p className="text-xs text-gray-400">{complex.prices.highestPriceDate}</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-400">현재가</p>
              <p className="text-sm font-bold text-blue-600">{formatPrice(complex.prices.current24py)}</p>
              <p className="text-xs text-gray-400">2025-05 (추정)</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-400">회복률</p>
              <p className={`text-sm font-bold ${complex.prices.recoveryRate >= 90 ? 'text-green-600' : complex.prices.recoveryRate >= 80 ? 'text-yellow-600' : 'text-red-600'}`}>
                {complex.prices.recoveryRate}%
              </p>
            </div>
          </div>
        </div>
        <PriceChart data={complex.prices.priceHistory} highestPrice={complex.prices.highestPrice24py} />
        <p className="text-xs text-gray-400 mt-2">* 모든 가격은 추정치. 국토부 실거래가 공개시스템 재확인 필요. 출처: {complex.prices.dataSource}</p>
      </div>

      {/* Reconstruction timeline */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
        <h2 className="text-lg font-black text-gray-900 mb-4">정비사업 진행 단계</h2>

        <div className="mb-4">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm font-medium text-gray-700">전체 진행률</span>
            <span className="text-sm font-bold text-blue-600">{progress}%</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-3">
            <div
              className="bg-blue-500 h-3 rounded-full transition-all duration-700"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="relative">
          <div className="absolute left-3 top-0 bottom-0 w-0.5 bg-gray-200" />
          <div className="space-y-3">
            {STAGE_STEPS.map((step, i) => {
              const stepCode = i + 1;
              const completed = stepCode < complex.reconstruction.stageCode;
              const current = stepCode === complex.reconstruction.stageCode;
              const future = stepCode > complex.reconstruction.stageCode;
              return (
                <div key={step} className="flex items-center gap-3 relative pl-7">
                  <div className={`absolute left-0 w-6 h-6 rounded-full border-2 flex items-center justify-center text-xs font-bold z-10 ${
                    completed ? 'bg-green-500 border-green-500 text-white'
                    : current ? 'bg-blue-500 border-blue-500 text-white'
                    : 'bg-white border-gray-300 text-gray-400'
                  }`}>
                    {completed ? '✓' : stepCode}
                  </div>
                  <span className={`text-sm font-medium ${
                    completed ? 'text-green-700'
                    : current ? 'text-blue-700 font-bold'
                    : 'text-gray-400'
                  }`}>
                    {step}
                    {current && <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">현재 단계</span>}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="mt-4 p-3 bg-blue-50 rounded-xl">
          <p className="text-xs text-blue-700">
            <strong>현재 단계:</strong> {complex.reconstruction.stage}<br />
            <strong>단계 설명:</strong> {complex.reconstruction.stageDetail}<br />
            <strong>예상 완공:</strong> {complex.reconstruction.expectedCompletion}<br />
            <strong>시공사:</strong> {complex.reconstruction.contractor}<br />
            <strong>예상 브랜드:</strong> {complex.reconstruction.expectedBrand}
          </p>
        </div>
        {!complex.reconstruction.verified && (
          <p className="text-xs text-yellow-700 mt-2 flex items-center gap-1">
            ⚠️ 사업 단계 정보 확인 필요: {complex.reconstruction.dataSource}
          </p>
        )}
      </div>

      {/* Financial simulation for this complex */}
      {complex.type === 'target' && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
          <h2 className="text-lg font-black text-gray-900 mb-4">자금 계획 (기본 시나리오)</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
            {[
              { label: '매수가 (추정)', value: formatPrice(f.targetPrice), color: 'text-gray-900' },
              { label: '취득세 (추정)', value: formatPrice(f.acquisitionTax), color: 'text-orange-600' },
              { label: '중개수수료', value: formatPrice(f.agencyFee), color: 'text-orange-600' },
              { label: '이사비+예비비', value: formatPrice(f.movingCost + f.contingency), color: 'text-orange-600' },
              { label: '총 필요 금액', value: formatPrice(f.totalRequired), color: 'text-red-600 font-black' },
              { label: '현재 자본(추정)', value: formatPrice(f.available), color: 'text-green-600 font-black' },
            ].map((item) => (
              <div key={item.label} className="bg-gray-50 rounded-xl p-3 text-center">
                <p className="text-xs text-gray-400 mb-1">{item.label}</p>
                <p className={`text-sm font-bold ${item.color}`}>{item.value}</p>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between p-3 rounded-xl border-2 border-blue-200 bg-blue-50">
            <div>
              <p className="text-sm text-gray-600">자금 여건</p>
              <p className="text-xs text-gray-400 mt-0.5">인덕원 12억 매도 + 현금 5억 + 대출 3억 기준</p>
            </div>
            <FeasibilityBadge status={f.status} />
          </div>

          <Link
            href="/simulation"
            className="block mt-3 text-center text-sm text-blue-600 hover:underline"
          >
            자금 조건 변경하여 재계산 →
          </Link>
        </div>
      )}

      {/* Scores */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
        <h2 className="text-lg font-black text-gray-900 mb-4">투자·거주 점수 분석</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-gray-700">투자 지표</h3>
            <ScoreBar label="종합 점수" score={complex.scores.overall} />
            <ScoreBar label="수익성 (사업성)" score={complex.scores.profitability} />
            <ScoreBar label="투자 매력도" score={complex.scores.investmentAttractiveness} />
            <ScoreBar label="리스크 (낮을수록 ↓)" score={complex.scores.risk} invertColor />
          </div>
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-gray-700">입지·거주 지표</h3>
            <ScoreBar label="입지 점수" score={complex.scores.location} />
            <ScoreBar label="교통 점수" score={complex.scores.transport} />
            <ScoreBar label="학군 점수" score={complex.scores.school} />
            <ScoreBar label="실거주 만족도" score={complex.scores.livingComfort} />
          </div>
        </div>
        <p className="text-xs text-gray-400 mt-4">* 점수는 정성적 평가 기준이며 주관적 가중치 포함. 참고 자료로만 활용하세요.</p>
      </div>

      {/* Pros / Cons / Risks */}
      <div className="grid sm:grid-cols-3 gap-4">
        <div className="bg-green-50 border border-green-200 rounded-2xl p-4">
          <h3 className="font-bold text-green-800 mb-3 flex items-center gap-1">
            <span>✅</span> 장점
          </h3>
          <ul className="space-y-2">
            {complex.pros.map((p, i) => (
              <li key={i} className="text-xs text-green-700 flex items-start gap-1.5">
                <span className="text-green-500 mt-0.5 flex-shrink-0">•</span>
                {p}
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-2xl p-4">
          <h3 className="font-bold text-yellow-800 mb-3 flex items-center gap-1">
            <span>⚠️</span> 단점
          </h3>
          <ul className="space-y-2">
            {complex.cons.map((c, i) => (
              <li key={i} className="text-xs text-yellow-700 flex items-start gap-1.5">
                <span className="text-yellow-500 mt-0.5 flex-shrink-0">•</span>
                {c}
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-2xl p-4">
          <h3 className="font-bold text-red-800 mb-3 flex items-center gap-1">
            <span>🔴</span> 리스크
          </h3>
          <ul className="space-y-2">
            {complex.risks.map((r, i) => (
              <li key={i} className="text-xs text-red-700 flex items-start gap-1.5">
                <span className="text-red-500 mt-0.5 flex-shrink-0">•</span>
                {r}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Wife persuasion */}
      {complex.wifePersuasionPoints.length > 0 && (
        <div className="bg-pink-50 border border-pink-200 rounded-2xl p-5">
          <h2 className="text-lg font-black text-pink-800 mb-3">💌 아내 설득 포인트</h2>
          <ul className="space-y-2">
            {complex.wifePersuasionPoints.map((p, i) => (
              <li key={i} className="text-sm text-pink-700 flex items-start gap-2">
                <span className="text-pink-400 text-lg leading-5">✦</span>
                {p}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Nearby schools */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
        <h2 className="text-lg font-black text-gray-900 mb-3">학군 정보</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <p className="text-sm font-bold text-gray-700 mb-2">인근 학교</p>
            <div className="space-y-2">
              {complex.location.nearbySchools.map((s) => (
                <div key={s.name} className="flex items-center gap-2">
                  <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${
                    s.type === '초' ? 'bg-green-100 text-green-700'
                    : s.type === '중' ? 'bg-blue-100 text-blue-700'
                    : 'bg-purple-100 text-purple-700'
                  }`}>{s.type}</span>
                  <span className="text-sm text-gray-700">{s.name}</span>
                  <span className="text-xs text-gray-400">약 {s.distanceM}m</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <p className="text-sm font-bold text-gray-700 mb-2">지하철 접근</p>
            <div className="space-y-2">
              {complex.location.subwayStations.map((s) => (
                <div key={s.name} className="flex items-center gap-2">
                  <span className="text-xs font-bold px-1.5 py-0.5 rounded bg-orange-100 text-orange-700">🚇</span>
                  <span className="text-sm text-gray-700">{s.name}</span>
                  <span className="text-xs text-gray-500">{s.line}</span>
                  <span className="text-xs text-gray-400">도보 {s.walkMinutes}분</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex gap-3 justify-between">
        <Link
          href="/compare"
          className="flex-1 text-center bg-gray-100 text-gray-700 rounded-xl py-3 font-bold hover:bg-gray-200 transition-colors"
        >
          ← 전체 비교
        </Link>
        <Link
          href="/simulation"
          className="flex-1 text-center bg-blue-600 text-white rounded-xl py-3 font-bold hover:bg-blue-700 transition-colors"
        >
          자금 시뮬레이션 →
        </Link>
      </div>

    </div>
  );
}
