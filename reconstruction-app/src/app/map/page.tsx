'use client';
import Link from 'next/link';
import { useState } from 'react';
import { TARGET_COMPLEXES, CURRENT_APARTMENT, getComparisonPrice, getComparisonSize } from '@/data/complexes';
import { formatPrice } from '@/data/calculations';
import StageBadge from '@/components/StageBadge';
import ScoreBar from '@/components/ScoreBar';

// 지도: 가락동/방이동 영역을 stylized SVG로 표현
// 실제 좌표를 [37.49~37.52, 127.11~127.14] 범위에 맞게 정규화

const MAP_BOUNDS = { latMin: 37.488, latMax: 37.525, lngMin: 127.105, lngMax: 127.148 };
const MAP_W = 700;
const MAP_H = 480;

function toXY(lat: number, lng: number): { x: number; y: number } {
  const x = ((lng - MAP_BOUNDS.lngMin) / (MAP_BOUNDS.lngMax - MAP_BOUNDS.lngMin)) * MAP_W;
  const y = MAP_H - ((lat - MAP_BOUNDS.latMin) / (MAP_BOUNDS.latMax - MAP_BOUNDS.latMin)) * MAP_H;
  return { x, y };
}

const SUBWAY_LINES: { name: string; line: string; lat: number; lng: number }[] = [
  { name: '가락시장역', line: '8호선', lat: 37.4997, lng: 127.1218 },
  { name: '송파역', line: '8호선', lat: 37.5038, lng: 127.1205 },
  { name: '방이역', line: '5호선', lat: 37.5158, lng: 127.1245 },
  { name: '올림픽공원역', line: '5·9호선', lat: 37.5213, lng: 127.1195 },
  { name: '잠실역', line: '2·8호선', lat: 37.5133, lng: 127.1001 },
];

const LANDMARKS = [
  { name: '헬리오시티', lat: 37.4967, lng: 127.1225, type: 'landmark' },
  { name: '올림픽공원', lat: 37.5208, lng: 127.1220, type: 'park' },
  { name: '롯데월드몰', lat: 37.5110, lng: 127.0980, type: 'mall' },
  { name: '가락시장', lat: 37.4970, lng: 127.1220, type: 'market' },
  { name: '문정법조타운', lat: 37.4800, lng: 127.1250, type: 'business' },
];

export default function MapPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  const allComplexes = [CURRENT_APARTMENT, ...TARGET_COMPLEXES];
  const selected = allComplexes.find((c) => c.id === selectedId);

  const markerColor = (id: string) => {
    if (id === 'indukwon-samsung') return '#6b7280';
    const c = TARGET_COMPLEXES.find((x) => x.id === id);
    if (!c) return '#3b82f6';
    if (c.recommendationRank === 1) return '#f59e0b';
    if (c.recommendationRank === 2) return '#3b82f6';
    if (c.recommendationRank === 3) return '#8b5cf6';
    return '#6b7280';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-black text-gray-900">지도로 보는 입지 비교</h1>
        <p className="text-gray-500 text-sm mt-1">
          * 개념도 수준의 시각화입니다. 정확한 위치는 네이버 지도·카카오 지도로 확인하세요.
        </p>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 mb-4">
        {[
          { color: '#6b7280', label: '현재 보유 (인덕원)' },
          { color: '#f59e0b', label: '1순위 추천' },
          { color: '#3b82f6', label: '2순위 추천' },
          { color: '#8b5cf6', label: '3순위 추천' },
          { color: '#6b7280', label: '4~5순위' },
        ].map((l) => (
          <div key={l.label} className="flex items-center gap-1.5 text-xs text-gray-600">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: l.color }} />
            {l.label}
          </div>
        ))}
      </div>

      <div className="flex flex-col lg:flex-row gap-4">
        {/* SVG Map */}
        <div className="flex-1 bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="overflow-x-auto scrollbar-hide">
            <svg
              viewBox={`0 0 ${MAP_W} ${MAP_H}`}
              className="w-full min-w-[320px]"
              style={{ minHeight: 280 }}
            >
              {/* Background */}
              <rect width={MAP_W} height={MAP_H} fill="#e8f0e8" />

              {/* Roads - horizontal */}
              <line x1="0" y1={toXY(37.503, 127.12).y} x2={MAP_W} y2={toXY(37.503, 127.12).y}
                stroke="#c8d8c8" strokeWidth="6" />
              <line x1="0" y1={toXY(37.513, 127.12).y} x2={MAP_W} y2={toXY(37.513, 127.12).y}
                stroke="#c8d8c8" strokeWidth="8" />

              {/* Roads - vertical */}
              <line x1={toXY(37.5, 127.1180).x} y1="0" x2={toXY(37.5, 127.1180).x} y2={MAP_H}
                stroke="#c8d8c8" strokeWidth="6" />
              <line x1={toXY(37.5, 127.123).x} y1="0" x2={toXY(37.5, 127.123).x} y2={MAP_H}
                stroke="#c8d8c8" strokeWidth="8" />

              {/* 올림픽공원 */}
              {(() => {
                const { x, y } = toXY(37.518, 127.122);
                return (
                  <ellipse cx={x} cy={y} rx={60} ry={45} fill="#86efac" opacity={0.8} />
                );
              })()}
              <text
                x={toXY(37.518, 127.122).x}
                y={toXY(37.518, 127.122).y + 4}
                textAnchor="middle" fontSize={10} fill="#166534" fontWeight="bold"
              >올림픽공원</text>

              {/* 헬리오시티 단지 */}
              {(() => {
                const { x, y } = toXY(37.4967, 127.1225);
                return (
                  <rect x={x - 28} y={y - 18} width={56} height={36} rx={4}
                    fill="#dbeafe" stroke="#93c5fd" strokeWidth={1.5} opacity={0.9} />
                );
              })()}
              <text
                x={toXY(37.4967, 127.1225).x}
                y={toXY(37.4967, 127.1225).y + 4}
                textAnchor="middle" fontSize={8} fill="#1e40af"
              >헬리오시티</text>

              {/* Subway line 8 */}
              <polyline
                points={[
                  toXY(37.4800, 127.1210),
                  toXY(37.4970, 127.1218),
                  toXY(37.5038, 127.1205),
                  toXY(37.5213, 127.119),
                ].map(({ x, y }) => `${x},${y}`).join(' ')}
                fill="none" stroke="#f97316" strokeWidth={3} strokeDasharray="0" opacity={0.8}
              />

              {/* Subway line 5 */}
              <polyline
                points={[
                  toXY(37.512, 127.098),
                  toXY(37.5158, 127.1245),
                  toXY(37.521, 127.131),
                ].map(({ x, y }) => `${x},${y}`).join(' ')}
                fill="none" stroke="#8b5cf6" strokeWidth={3} opacity={0.8}
              />

              {/* Subway stations */}
              {SUBWAY_LINES.map((s) => {
                const { x, y } = toXY(s.lat, s.lng);
                return (
                  <g key={s.name}>
                    <circle cx={x} cy={y} r={7} fill="white" stroke="#374151" strokeWidth={1.5} />
                    <text x={x} y={y + 16} textAnchor="middle" fontSize={8} fill="#374151">{s.name}</text>
                  </g>
                );
              })}

              {/* Complex markers */}
              {allComplexes.map((complex) => {
                const { x, y } = toXY(complex.location.lat, complex.location.lng);
                const color = markerColor(complex.id);
                const isSelected = selectedId === complex.id;
                const isHovered = hoveredId === complex.id;
                const isInDukwon = complex.id === 'indukwon-samsung';

                if (isInDukwon) return null; // 인덕원은 다른 좌표계 (서울 밖)

                return (
                  <g
                    key={complex.id}
                    onClick={() => setSelectedId(selectedId === complex.id ? null : complex.id)}
                    onMouseEnter={() => setHoveredId(complex.id)}
                    onMouseLeave={() => setHoveredId(null)}
                    style={{ cursor: 'pointer' }}
                  >
                    <circle
                      cx={x} cy={y}
                      r={isSelected || isHovered ? 16 : 12}
                      fill={color}
                      stroke="white"
                      strokeWidth={2.5}
                      opacity={0.9}
                    />
                    <text x={x} y={y + 4} textAnchor="middle" fontSize={10} fill="white" fontWeight="bold">
                      {complex.recommendationRank}
                    </text>
                    <text x={x} y={y + 24} textAnchor="middle" fontSize={9} fill="#1f2937" fontWeight="600">
                      {complex.shortName}
                    </text>
                    <text x={x} y={y + 35} textAnchor="middle" fontSize={8} fill="#6b7280">
                      {formatPrice(getComparisonPrice(complex))}
                    </text>

                    {/* Popup on hover */}
                    {isHovered && (
                      <g>
                        <rect x={x - 60} y={y - 65} width={120} height={52} rx={6}
                          fill="#1f2937" opacity={0.95} />
                        <text x={x} y={y - 45} textAnchor="middle" fontSize={9} fill="white" fontWeight="bold">
                          {complex.shortName}
                        </text>
                        <text x={x} y={y - 30} textAnchor="middle" fontSize={8} fill="#d1d5db">
                          {formatPrice(getComparisonPrice(complex))} ({getComparisonSize(complex)})
                        </text>
                        <text x={x} y={y - 18} textAnchor="middle" fontSize={7} fill="#9ca3af">
                          클릭하여 상세 보기
                        </text>
                      </g>
                    )}
                  </g>
                );
              })}

              {/* Labels */}
              <text x={10} y={20} fontSize={9} fill="#4b5563">8호선</text>
              <rect x={8} y={10} width={8} height={4} fill="#f97316" />
              <text x={10} y={35} fontSize={9} fill="#4b5563">5호선</text>
              <rect x={8} y={25} width={8} height={4} fill="#8b5cf6" />

              {/* 방이동/가락동 labels */}
              <text x={toXY(37.515, 127.115).x} y={toXY(37.515, 127.115).y}
                fontSize={11} fill="#374151" fontWeight="600" opacity={0.6}>방이동</text>
              <text x={toXY(37.500, 127.118).x} y={toXY(37.500, 127.118).y}
                fontSize={11} fill="#374151" fontWeight="600" opacity={0.6}>가락동</text>
            </svg>
          </div>

          {/* 인덕원 위치 안내 */}
          <div className="p-3 bg-gray-50 border-t border-gray-100">
            <p className="text-xs text-gray-500 flex items-center gap-1">
              <span className="w-3 h-3 rounded-full bg-gray-400 inline-block" />
              현재 보유 (인덕원마을삼성)은 경기도 안양시에 위치하여 지도 범위 밖입니다.
              서울 송파구와 직선 거리 약 25km.
            </p>
          </div>
        </div>

        {/* Side panel */}
        <div className="lg:w-80 space-y-3">
          {selected ? (
            <div className="bg-white rounded-2xl shadow-sm border border-blue-200 p-5">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-black text-gray-900 text-lg">{selected.shortName}</h3>
                  <p className="text-xs text-gray-500">{selected.location.address}</p>
                </div>
                <button
                  onClick={() => setSelectedId(null)}
                  className="text-gray-400 hover:text-gray-600 text-lg"
                >×</button>
              </div>

              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-gray-50 rounded-lg p-2 text-center">
                  <p className="text-xs text-gray-400">{getComparisonSize(selected)} 현재가</p>
                  <p className="font-black text-gray-900 text-sm">{formatPrice(getComparisonPrice(selected))}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-2 text-center">
                  <p className="text-xs text-gray-400">세대수</p>
                  <p className="font-black text-gray-900 text-sm">{selected.basicInfo.totalUnits.toLocaleString()}세대</p>
                </div>
              </div>

              <div className="mb-3">
                <StageBadge stageCode={selected.reconstruction.stageCode} />
              </div>

              <div className="space-y-2 mb-4">
                <ScoreBar label="종합 점수" score={selected.scores.overall} />
                <ScoreBar label="입지" score={selected.scores.location} />
                <ScoreBar label="교통" score={selected.scores.transport} />
                <ScoreBar label="학군" score={selected.scores.school} />
                <ScoreBar label="수익성" score={selected.scores.profitability} />
              </div>

              <div className="mb-3">
                <p className="text-xs font-bold text-gray-700 mb-1">지하철 접근</p>
                {selected.location.subwayStations.map((s) => (
                  <p key={s.name} className="text-xs text-gray-600">
                    🚇 {s.name} ({s.line}) 도보 {s.walkMinutes}분
                  </p>
                ))}
              </div>

              <Link
                href={`/complex/${selected.id}`}
                className="block w-full text-center bg-blue-600 text-white rounded-xl py-2.5 text-sm font-bold hover:bg-blue-700 transition-colors"
              >
                상세 분석 보기 →
              </Link>
            </div>
          ) : (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
              <h3 className="font-bold text-gray-700 mb-3">단지 목록</h3>
              <p className="text-xs text-gray-400 mb-3">지도의 마커를 클릭하거나 아래에서 선택하세요</p>
              <div className="space-y-2">
                {TARGET_COMPLEXES.sort((a, b) => a.recommendationRank - b.recommendationRank).map((c) => (
                  <button
                    key={c.id}
                    onClick={() => setSelectedId(c.id)}
                    className="w-full text-left flex items-center gap-3 p-2.5 rounded-lg hover:bg-blue-50 transition-colors group"
                  >
                    <div
                      className="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-black flex-shrink-0"
                      style={{ backgroundColor: markerColor(c.id) }}
                    >
                      {c.recommendationRank}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-bold text-gray-800 text-sm group-hover:text-blue-700">{c.shortName}</p>
                      <p className="text-xs text-gray-400">{formatPrice(getComparisonPrice(c))} ({getComparisonSize(c)}) · {c.location.neighborhood}</p>
                    </div>
                    <StageBadge stageCode={c.reconstruction.stageCode} />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* 입지 접근성 요약 */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
            <h3 className="font-bold text-gray-700 mb-3 text-sm">📍 생활 인프라 (공통)</h3>
            <div className="space-y-2 text-xs text-gray-600">
              <div className="flex items-start gap-2">
                <span className="text-green-600 font-bold flex-shrink-0">✓</span>
                <span>올림픽공원 (88만m²) — 방이동 단지 5~15분</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-green-600 font-bold flex-shrink-0">✓</span>
                <span>헬리오시티(9,510세대) 생활인프라 — 가락동 단지 공유</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-green-600 font-bold flex-shrink-0">✓</span>
                <span>문정 법조타운·롯데몰 문정 — 업무·쇼핑 접근</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-green-600 font-bold flex-shrink-0">✓</span>
                <span>잠실 롯데월드몰·석촌호수 — 15~20분 접근</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-blue-600 font-bold flex-shrink-0">i</span>
                <span>서울아산병원 (암사동) 8호선 30분 이내</span>
              </div>
            </div>
          </div>

          {/* 인덕원 vs 송파 접근성 */}
          <div className="bg-orange-50 border border-orange-200 rounded-2xl p-4">
            <h3 className="font-bold text-orange-800 text-sm mb-2">인덕원 vs 송파 비교</h3>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-600">강남까지</span>
                <span className="text-orange-700 font-bold">인덕원 25분 vs 송파 20분</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">서울 핵심 입지</span>
                <span className="text-orange-700 font-bold">인덕원 경기 vs 송파 서울</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">재건축 브랜드</span>
                <span className="text-orange-700 font-bold">인덕원 리모델링 vs 송파 재건축</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">장기 희소성</span>
                <span className="text-orange-700 font-bold">인덕원 보통 vs 송파 높음</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
