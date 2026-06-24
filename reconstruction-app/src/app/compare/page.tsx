'use client';
import Link from 'next/link';
import { useState } from 'react';
import { TARGET_COMPLEXES, CURRENT_APARTMENT, getComparisonPrice } from '@/data/complexes';
import { formatPrice, calcFeasibility, DEFAULT_SIMULATION } from '@/data/calculations';
import StageBadge from '@/components/StageBadge';
import FeasibilityBadge from '@/components/FeasibilityBadge';
import ScoreBar from '@/components/ScoreBar';

type SortKey = 'rank' | 'price' | 'score' | 'stage' | 'units';

export default function ComparePage() {
  const [sortKey, setSortKey] = useState<SortKey>('rank');

  const feasibilities = TARGET_COMPLEXES.map((c) => ({
    id: c.id,
    ...calcFeasibility(c, DEFAULT_SIMULATION),
  }));

  const sorted = [...TARGET_COMPLEXES].sort((a, b) => {
    if (sortKey === 'rank') return a.recommendationRank - b.recommendationRank;
    if (sortKey === 'price') return getComparisonPrice(a) - getComparisonPrice(b);
    if (sortKey === 'score') return b.scores.overall - a.scores.overall;
    if (sortKey === 'stage') return b.reconstruction.stageCode - a.reconstruction.stageCode;
    if (sortKey === 'units') return b.basicInfo.totalUnits - a.basicInfo.totalUnits;
    return 0;
  });

  const allComplexes = [CURRENT_APARTMENT, ...TARGET_COMPLEXES];

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-black text-gray-900">전체 비교 테이블</h1>
          <p className="text-gray-500 text-sm">인덕원삼성 포함 6개 단지 비교 · 모든 가격 추정치</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">정렬:</span>
          {([
            ['rank', '추천순'],
            ['price', '가격순'],
            ['score', '점수순'],
            ['stage', '사업단계'],
            ['units', '세대수'],
          ] as [SortKey, string][]).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setSortKey(key)}
              className={`text-xs px-2.5 py-1 rounded-full font-medium transition-colors ${
                sortKey === key
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-3 text-xs text-yellow-700">
        ⚠️ 모든 가격, 사업 단계, 세대수 정보는 추정치입니다. 실제 투자 전 국토부 실거래가 공개시스템 및 서울시 정비사업 정보몽땅에서 재확인하세요.
      </div>

      {/* Main comparison table - horizontal scroll */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto scrollbar-hide">
          <table className="w-full text-sm min-w-[900px]">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="text-left py-3 px-4 text-gray-500 font-medium sticky left-0 bg-gray-50 min-w-[110px]">단지명</th>
                <th className="text-center py-3 px-3 text-gray-500 font-medium">현재가(인덕원 24평/송파 32평)</th>
                <th className="text-center py-3 px-3 text-gray-500 font-medium">세대수</th>
                <th className="text-center py-3 px-3 text-gray-500 font-medium">준공</th>
                <th className="text-center py-3 px-3 text-gray-500 font-medium">용적률</th>
                <th className="text-center py-3 px-3 text-gray-500 font-medium">재건후세대</th>
                <th className="text-center py-3 px-3 text-gray-500 font-medium">사업단계</th>
                <th className="text-center py-3 px-3 text-gray-500 font-medium">예상완공</th>
                <th className="text-center py-3 px-3 text-gray-500 font-medium">자금여건</th>
                <th className="text-center py-3 px-3 text-gray-500 font-medium">종합점수</th>
                <th className="text-center py-3 px-3 text-gray-500 font-medium">추천순위</th>
                <th className="text-center py-3 px-3 text-gray-500 font-medium">상세</th>
              </tr>
            </thead>
            <tbody>
              {/* 현재 보유 단지 */}
              <tr className="border-b border-gray-100 bg-gray-50">
                <td className="py-3 px-4 sticky left-0 bg-gray-50">
                  <div>
                    <p className="font-bold text-gray-600 text-xs">현재 보유</p>
                    <p className="font-black text-gray-800">{CURRENT_APARTMENT.shortName}</p>
                    <p className="text-xs text-gray-400">{CURRENT_APARTMENT.location.neighborhood}</p>
                  </div>
                </td>
                <td className="py-3 px-3 text-center font-bold text-gray-700">
                  {formatPrice(CURRENT_APARTMENT.prices.current24py)}<span className="text-xs text-gray-400 ml-1">24평</span>
                </td>
                <td className="py-3 px-3 text-center text-gray-600">
                  {CURRENT_APARTMENT.basicInfo.totalUnits.toLocaleString()}
                </td>
                <td className="py-3 px-3 text-center text-gray-600">{CURRENT_APARTMENT.basicInfo.builtYear}</td>
                <td className="py-3 px-3 text-center text-gray-600">{CURRENT_APARTMENT.basicInfo.floorAreaRatio}%</td>
                <td className="py-3 px-3 text-center text-gray-400 text-xs">리모델링</td>
                <td className="py-3 px-3 text-center">
                  <StageBadge stageCode={CURRENT_APARTMENT.reconstruction.stageCode} />
                </td>
                <td className="py-3 px-3 text-center text-xs text-gray-400">
                  {CURRENT_APARTMENT.reconstruction.expectedCompletion}
                </td>
                <td className="py-3 px-3 text-center text-xs text-gray-400">기준점</td>
                <td className="py-3 px-3 text-center">
                  <span className="font-bold text-gray-500">{CURRENT_APARTMENT.scores.overall}</span>
                </td>
                <td className="py-3 px-3 text-center text-xs text-gray-400">—</td>
                <td className="py-3 px-3 text-center">
                  <Link
                    href={`/complex/${CURRENT_APARTMENT.id}`}
                    className="text-xs text-blue-600 hover:underline"
                  >상세</Link>
                </td>
              </tr>

              {/* Target complexes */}
              {sorted.map((complex) => {
                const f = feasibilities.find((f) => f.id === complex.id)!;
                const rankColors = ['', 'text-yellow-600', 'text-gray-500', 'text-amber-700', 'text-slate-500', 'text-slate-400'];
                return (
                  <tr key={complex.id} className="border-b border-gray-50 hover:bg-blue-50 transition-colors">
                    <td className="py-3 px-4 sticky left-0 bg-white hover:bg-blue-50 transition-colors">
                      <div>
                        <p className={`text-xs font-bold ${rankColors[complex.recommendationRank]}`}>
                          {complex.recommendationRank}순위
                        </p>
                        <p className="font-black text-gray-900">{complex.shortName}</p>
                        <p className="text-xs text-gray-400">{complex.location.neighborhood}</p>
                      </div>
                    </td>
                    <td className="py-3 px-3 text-center">
                      <span className="font-black text-gray-900">{formatPrice(getComparisonPrice(complex))}</span>
                      <p className="text-xs text-gray-400">32평 · 확인 필요</p>
                    </td>
                    <td className="py-3 px-3 text-center text-gray-700">
                      {complex.basicInfo.totalUnits.toLocaleString()}
                    </td>
                    <td className="py-3 px-3 text-center text-gray-600">{complex.basicInfo.builtYear}</td>
                    <td className="py-3 px-3 text-center">
                      <span className="text-gray-700">{complex.basicInfo.floorAreaRatio}%</span>
                      <p className="text-xs text-blue-500">→{complex.reconstruction.expectedFARAfter}%</p>
                    </td>
                    <td className="py-3 px-3 text-center">
                      <span className="text-gray-700">{complex.reconstruction.expectedUnitsAfter.toLocaleString()}</span>
                      <p className="text-xs text-gray-400">일반 {complex.reconstruction.generalSaleUnits}</p>
                    </td>
                    <td className="py-3 px-3 text-center">
                      <StageBadge stageCode={complex.reconstruction.stageCode} />
                    </td>
                    <td className="py-3 px-3 text-center text-xs text-gray-600">
                      {complex.reconstruction.expectedCompletion}
                    </td>
                    <td className="py-3 px-3 text-center">
                      <FeasibilityBadge status={f.status} />
                    </td>
                    <td className="py-3 px-3 text-center">
                      <div className="flex flex-col items-center gap-1">
                        <span className={`text-lg font-black ${
                          complex.scores.overall >= 80 ? 'text-green-600'
                          : complex.scores.overall >= 70 ? 'text-blue-600'
                          : 'text-yellow-600'
                        }`}>{complex.scores.overall}</span>
                        <div className="w-16">
                          <div className="w-full bg-gray-100 rounded-full h-1.5">
                            <div
                              className="bg-blue-500 h-1.5 rounded-full"
                              style={{ width: `${complex.scores.overall}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-3 text-center">
                      <span className={`text-lg font-black ${rankColors[complex.recommendationRank]}`}>
                        {complex.recommendationRank}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-center">
                      <Link
                        href={`/complex/${complex.id}`}
                        className="text-xs text-blue-600 hover:underline font-medium"
                      >상세 →</Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Score comparison cards */}
      <div>
        <h2 className="text-xl font-black text-gray-900 mb-4">항목별 점수 비교</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {(['location', 'school', 'transport', 'profitability', 'risk', 'overall'] as const).map((scoreKey) => {
            const labels: Record<string, string> = {
              location: '입지 점수',
              school: '학군 점수',
              transport: '교통 점수',
              profitability: '수익성 점수',
              risk: '리스크 (낮을수록 좋음)',
              overall: '종합 추천 점수',
            };
            const isRisk = scoreKey === 'risk';
            const sortedByScore = [...allComplexes].sort((a, b) =>
              isRisk
                ? a.scores[scoreKey] - b.scores[scoreKey]
                : b.scores[scoreKey] - a.scores[scoreKey]
            );
            return (
              <div key={scoreKey} className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
                <h3 className="text-sm font-bold text-gray-700 mb-3">{labels[scoreKey]}</h3>
                <div className="space-y-2">
                  {sortedByScore.map((c, idx) => (
                    <div key={c.id} className="flex items-center gap-2">
                      <span className="text-xs text-gray-400 w-4">{idx + 1}</span>
                      <span className={`text-xs font-medium w-16 flex-shrink-0 ${c.type === 'current' ? 'text-gray-500' : 'text-gray-800'}`}>
                        {c.shortName}
                      </span>
                      <div className="flex-1">
                        <ScoreBar
                          label=""
                          score={c.scores[scoreKey]}
                          invertColor={isRisk}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Subway access comparison */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
        <h2 className="text-lg font-black text-gray-900 mb-4">교통 접근성 비교</h2>
        <div className="overflow-x-auto scrollbar-hide">
          <table className="w-full text-sm min-w-[600px]">
            <thead className="border-b border-gray-100">
              <tr>
                <th className="text-left py-2 px-3 text-gray-500 font-medium">단지</th>
                <th className="text-center py-2 px-3 text-gray-500 font-medium">지하철역</th>
                <th className="text-center py-2 px-3 text-gray-500 font-medium">노선</th>
                <th className="text-center py-2 px-3 text-gray-500 font-medium">도보</th>
              </tr>
            </thead>
            <tbody>
              {allComplexes.map((complex) =>
                complex.location.subwayStations.map((s, i) => (
                  <tr key={`${complex.id}-${s.name}`} className="border-b border-gray-50 hover:bg-gray-50">
                    {i === 0 && (
                      <td rowSpan={complex.location.subwayStations.length} className="py-2 px-3 font-medium text-gray-800">
                        {complex.shortName}
                      </td>
                    )}
                    <td className="py-2 px-3 text-center text-gray-700">{s.name}</td>
                    <td className="py-2 px-3 text-center">
                      <span className="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full">{s.line}</span>
                    </td>
                    <td className="py-2 px-3 text-center">
                      <span className={`text-xs font-bold ${s.walkMinutes <= 5 ? 'text-green-600' : s.walkMinutes <= 10 ? 'text-blue-600' : 'text-yellow-600'}`}>
                        {s.walkMinutes}분
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Reconstruction info comparison */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
        <h2 className="text-lg font-black text-gray-900 mb-4">재건축 정보 비교</h2>
        <div className="overflow-x-auto scrollbar-hide">
          <table className="w-full text-sm min-w-[700px]">
            <thead className="border-b border-gray-100">
              <tr>
                <th className="text-left py-2 px-3 text-gray-500 font-medium">단지</th>
                <th className="text-center py-2 px-3 text-gray-500 font-medium">사업 단계</th>
                <th className="text-center py-2 px-3 text-gray-500 font-medium">조합설립</th>
                <th className="text-center py-2 px-3 text-gray-500 font-medium">현재→재건후 세대</th>
                <th className="text-center py-2 px-3 text-gray-500 font-medium">일반분양</th>
                <th className="text-center py-2 px-3 text-gray-500 font-medium">예상 시공사</th>
                <th className="text-center py-2 px-3 text-gray-500 font-medium">예상 완공</th>
              </tr>
            </thead>
            <tbody>
              {TARGET_COMPLEXES.sort((a, b) => a.recommendationRank - b.recommendationRank).map((complex) => (
                <tr key={complex.id} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="py-2.5 px-3 font-bold text-gray-900">{complex.shortName}</td>
                  <td className="py-2.5 px-3 text-center">
                    <StageBadge stageCode={complex.reconstruction.stageCode} />
                  </td>
                  <td className="py-2.5 px-3 text-center">
                    {complex.reconstruction.associationEstablished
                      ? <span className="text-green-600 font-bold">완료</span>
                      : <span className="text-gray-400 text-xs">미완료</span>}
                  </td>
                  <td className="py-2.5 px-3 text-center text-gray-700">
                    {complex.basicInfo.totalUnits.toLocaleString()} → {complex.reconstruction.expectedUnitsAfter.toLocaleString()}
                    <span className="text-xs text-green-600 ml-1">
                      (+{(complex.reconstruction.expectedUnitsAfter - complex.basicInfo.totalUnits).toLocaleString()})
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-center text-gray-700">
                    {complex.reconstruction.generalSaleUnits.toLocaleString()}세대
                  </td>
                  <td className="py-2.5 px-3 text-center text-xs text-gray-600">
                    {complex.reconstruction.contractor}
                  </td>
                  <td className="py-2.5 px-3 text-center text-xs text-gray-600">
                    {complex.reconstruction.expectedCompletion}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-gray-400 mt-3">* 모든 재건축 정보는 추정치 — 서울시 정비사업 정보몽땅 및 해당 구청 공식 자료 재확인 필요</p>
      </div>

    </div>
  );
}
