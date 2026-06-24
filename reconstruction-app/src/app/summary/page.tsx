import Link from 'next/link';
import { TARGET_COMPLEXES, CURRENT_APARTMENT, getComparisonPrice, getComparisonSize } from '@/data/complexes';
import { formatPrice, calcFeasibility, DEFAULT_SIMULATION, calcOpportunityCost } from '@/data/calculations';
import FeasibilityBadge from '@/components/FeasibilityBadge';
import StageBadge from '@/components/StageBadge';
import ScoreBar from '@/components/ScoreBar';

const sorted = [...TARGET_COMPLEXES].sort((a, b) => a.recommendationRank - b.recommendationRank);

export default function SummaryPage() {
  const feasibilities = sorted.map((c) => ({
    id: c.id,
    ...calcFeasibility(c, DEFAULT_SIMULATION),
  }));

  // 기회비용 계산 (10년 기준, 인덕원 3% vs 송파 6% 연평균 상승 가정)
  const opp = calcOpportunityCost(
    CURRENT_APARTMENT.prices.current24py,
    getComparisonPrice(sorted[0]),
    10,
    6,
    3
  );

  const top3 = sorted.slice(0, 3);

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 space-y-8">

      {/* Header */}
      <div className="text-center">
        <p className="text-blue-600 font-bold text-sm mb-2">의사결정 보조 요약</p>
        <h1 className="text-3xl font-black text-gray-900 leading-tight">
          지금 갈아타야 하는가?
        </h1>
        <p className="text-gray-500 mt-2">
          숫자와 논리로 보는 갈아타기 의사결정 근거 — 투자 권유 아님
        </p>
      </div>

      {/* Warning */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-2xl p-4 text-sm text-yellow-800">
        <strong>⚠️ 중요:</strong> 본 요약의 모든 가격·수치는 추정치입니다. 실제 거래 전 반드시 공식 자료를 재확인하세요.
        이 앱은 의사결정 보조 도구이며 투자 권유가 아닙니다.
      </div>

      {/* 왜 지금 고민해야 하는가 */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-xl font-black text-gray-900 mb-4">① 왜 지금 갈아타기를 검토해야 하는가</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          {[
            {
              icon: '📍',
              title: '서울 vs 경기 입지 격차',
              body: '인덕원(안양시)과 송파구는 행정구역뿐 아니라 자산가치 상승 동력이 다릅니다. 서울 핵심 권역의 희소성은 장기적으로 확대될 가능성이 높습니다.',
            },
            {
              icon: '🏗️',
              title: '재건축 vs 리모델링',
              body: '인덕원삼성은 리모델링 추진 중입니다. 리모델링은 재건축 대비 시세 상승 폭이 제한적이며, 준공 후에도 "신축"으로 인정되지 않습니다.',
            },
            {
              icon: '⏰',
              title: '타이밍: 전고점 대비 조정 국면',
              body: '가락동 단지들은 전고점(2021년) 대비 83~85% 수준에 머물고 있습니다. 재건축 진행에 따른 이슈프리미엄 반영 전에 진입하는 것이 유리할 수 있습니다.',
            },
            {
              icon: '🎓',
              title: '자녀 교육·생활권',
              body: '송파구는 강남 3구에 준하는 교육 인프라를 갖추고 있습니다. 잠실·방이·가락의 생활권은 아이 성장에 유리한 환경을 제공합니다.',
            },
          ].map((item) => (
            <div key={item.title} className="flex gap-3 p-4 bg-gray-50 rounded-xl">
              <span className="text-2xl flex-shrink-0">{item.icon}</span>
              <div>
                <h3 className="font-bold text-gray-800 text-sm mb-1">{item.title}</h3>
                <p className="text-xs text-gray-600 leading-relaxed">{item.body}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 기회비용 */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-xl font-black text-gray-900 mb-4">② 인덕원 보유의 기회비용 (10년 시뮬레이션)</h2>
        <div className="bg-orange-50 border border-orange-200 rounded-xl p-4 mb-4">
          <p className="text-xs text-orange-700 mb-2">
            가정: 인덕원삼성 연 3% 상승 vs 올림픽훼밀리 연 6% 상승 (재건축 프리미엄 포함 추정) — 실제 수익 보장 아님
          </p>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-xs text-gray-500">인덕원 보유 시 (10년 후)</p>
              <p className="text-lg font-black text-gray-700">{formatPrice(opp.indukwonFinal)}</p>
              <p className="text-xs text-gray-400">연 3% 가정</p>
            </div>
            <div className="flex items-center justify-center">
              <span className="text-gray-400">→</span>
            </div>
            <div>
              <p className="text-xs text-gray-500">올림픽훼밀리 갈아타기 (10년 후)</p>
              <p className="text-lg font-black text-blue-700">{formatPrice(opp.targetFinal)}</p>
              <p className="text-xs text-gray-400">연 6% 가정</p>
            </div>
          </div>
          <div className="mt-3 text-center">
            <p className="text-xs text-gray-500">예상 차이</p>
            <p className="text-2xl font-black text-green-600">+{formatPrice(opp.difference)}</p>
            <p className="text-xs text-gray-400 mt-1">* 상승률 가정은 미래 수익 보장 아님. 참고용 시뮬레이션입니다.</p>
          </div>
        </div>
        <p className="text-xs text-gray-500 bg-gray-50 rounded-lg p-3">
          기회비용의 핵심은 "지금 12억짜리 인덕원을 들고 있는 것 vs 18~20억짜리 송파 재건축에 투자하는 것"의 차이입니다.
          물론 대출 비용, 이자, 주거 불편 등 추가 비용도 고려해야 합니다.
        </p>
      </div>

      {/* 송파 재건축의 희소성 */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-xl font-black text-gray-900 mb-4">③ 송파 재건축의 장기 희소성</h2>
        <div className="space-y-3">
          {[
            { icon: '🏆', text: '서울 강남권 (강남·서초·송파) 내 재건축 가능 부지는 절대적으로 희소합니다. 새로운 공급이 없는 상황에서 완공 후 시세는 인근 신축 대비 프리미엄이 예상됩니다.' },
            { icon: '🌿', text: '올림픽공원(88만m²) 인접 입지는 대체 불가능한 조건입니다. 완공 후 "올림픽공원 바로 옆 브랜드 신축 아파트"는 서울에서 손꼽히는 희소 자산이 될 수 있습니다.' },
            { icon: '🚇', text: '5호선·8호선 등 복수 지하철 접근성은 강남·여의도·도심 모두로의 접근을 용이하게 합니다. 재건축 완공 후 교통 프리미엄은 더욱 강화될 것입니다.' },
            { icon: '🏫', text: '송파구 학군은 강남 3구 수준을 유지하고 있어 자녀 교육 측면에서도 장기 메리트가 있습니다.' },
          ].map((item, i) => (
            <div key={i} className="flex gap-3 items-start">
              <span className="text-xl flex-shrink-0">{item.icon}</span>
              <p className="text-sm text-gray-700 leading-relaxed">{item.text}</p>
            </div>
          ))}
        </div>
      </div>

      {/* 무리하지 않는 예산 상한선 */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-xl font-black text-gray-900 mb-4">④ 무리하지 않는 예산 상한선</h2>
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-4">
          <p className="font-bold text-blue-800 mb-2">권장 매수가 기준 (인덕원 12억 매도, 현금 5억, 대출 3억 기준)</p>
          <div className="grid sm:grid-cols-3 gap-3">
            <div className="bg-green-100 rounded-lg p-3 text-center">
              <p className="text-xs text-green-700">여유 있게 가능</p>
              <p className="text-lg font-black text-green-800">~15억</p>
              <p className="text-xs text-green-600">대출 1억 이하</p>
            </div>
            <div className="bg-blue-100 rounded-lg p-3 text-center">
              <p className="text-xs text-blue-700">대출 포함 가능</p>
              <p className="text-lg font-black text-blue-800">~18억</p>
              <p className="text-xs text-blue-600">대출 3~4억</p>
            </div>
            <div className="bg-yellow-100 rounded-lg p-3 text-center">
              <p className="text-xs text-yellow-700">주의 필요</p>
              <p className="text-lg font-black text-yellow-800">~20억</p>
              <p className="text-xs text-yellow-600">대출 5억 이상</p>
            </div>
          </div>
        </div>
        <p className="text-sm text-gray-600">
          "무조건 사자"가 아닌 <strong>"이 가격 이하라면 검토 가치 있음"</strong> 기준:
          가락동 단지들은 14~15억 이하에서 진입 시 큰 부담 없이 자금 계획 가능합니다.
          올림픽훼밀리타운은 장기 메리트가 있으나 추가 대출 부담을 고려해야 합니다.
        </p>
      </div>

      {/* 추천 순위 */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-xl font-black text-gray-900 mb-4">⑤ 최종 추천 (의견, 투자 권유 아님)</h2>
        <div className="space-y-4">
          {top3.map((complex, i) => {
            const f = feasibilities.find((f) => f.id === complex.id)!;
            const rankColors = ['bg-yellow-500', 'bg-gray-400', 'bg-amber-700'];
            const rankLabel = ['1순위', '2순위', '3순위'];
            return (
              <div key={complex.id} className="border border-gray-200 rounded-2xl p-4">
                <div className="flex items-start gap-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-black text-lg flex-shrink-0 ${rankColors[i]}`}>
                    {i + 1}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <h3 className="font-black text-gray-900 text-lg">{complex.name}</h3>
                      <StageBadge stageCode={complex.reconstruction.stageCode} />
                      <FeasibilityBadge status={f.status} />
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{complex.recommendationSummary}</p>
                    <div className="flex items-center gap-4 text-sm">
                      <div>
                        <span className="text-gray-400 text-xs">{getComparisonSize(complex)}(추정) </span>
                        <span className="font-bold text-gray-900">{formatPrice(getComparisonPrice(complex))}</span>
                      </div>
                      <div>
                        <span className="text-gray-400 text-xs">종합 점수 </span>
                        <span className="font-bold text-blue-600">{complex.scores.overall}점</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="mt-3 grid sm:grid-cols-3 gap-3">
                  <div>
                    <p className="text-xs font-bold text-green-700 mb-1">✅ 핵심 장점</p>
                    <ul className="text-xs text-gray-600 space-y-0.5">
                      {complex.pros.slice(0, 2).map((p, j) => <li key={j}>• {p}</li>)}
                    </ul>
                  </div>
                  <div>
                    <p className="text-xs font-bold text-yellow-700 mb-1">⚠️ 주요 단점</p>
                    <ul className="text-xs text-gray-600 space-y-0.5">
                      {complex.cons.slice(0, 2).map((c, j) => <li key={j}>• {c}</li>)}
                    </ul>
                  </div>
                  <div>
                    <p className="text-xs font-bold text-pink-700 mb-1">💌 아내 설득</p>
                    <ul className="text-xs text-gray-600 space-y-0.5">
                      {complex.wifePersuasionPoints.slice(0, 2).map((p, j) => <li key={j}>• {p}</li>)}
                    </ul>
                  </div>
                </div>
                <Link
                  href={`/complex/${complex.id}`}
                  className="block mt-3 text-center text-xs text-blue-600 hover:underline"
                >
                  {complex.shortName} 상세 분석 보기 →
                </Link>
              </div>
            );
          })}
        </div>
      </div>

      {/* 최악의 경우 리스크 */}
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6">
        <h2 className="text-xl font-black text-red-800 mb-4">⑥ 최악의 경우 리스크</h2>
        <div className="space-y-3">
          {[
            { risk: '재건축 사업 지연', detail: '재건축 사업은 조합 내부 갈등, 정부 규제 변화, 경기 침체 등으로 10년 이상 지연될 수 있습니다. 그 기간 동안 노후 단지에서 생활해야 합니다.' },
            { risk: '재건축 초과이익 환수제', detail: '재건축 완료 후 조합원 이익의 일부를 국가가 환수하는 제도가 적용될 수 있습니다. 예상 수익이 줄어들 수 있습니다.' },
            { risk: '부동산 시장 전반 하락', detail: '금리 인상, 경기 침체 등으로 서울 부동산 전반이 하락할 경우 단기적으로 자산 가치가 감소할 수 있습니다.' },
            { risk: '대출 이자 부담', detail: '추가 대출 시 금리 변동에 따른 이자 부담이 증가할 수 있습니다. DSR 한도 내에서 상환 능력을 충분히 검토하세요.' },
          ].map((item) => (
            <div key={item.risk} className="flex gap-3 items-start">
              <span className="text-red-500 font-bold text-sm flex-shrink-0">⚡</span>
              <div>
                <p className="font-bold text-red-800 text-sm">{item.risk}</p>
                <p className="text-xs text-red-700 mt-0.5">{item.detail}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 그래도 들어가도 되는 이유 */}
      <div className="bg-green-50 border border-green-200 rounded-2xl p-6">
        <h2 className="text-xl font-black text-green-800 mb-4">⑦ 그래도 검토 가치가 있는 이유</h2>
        <div className="space-y-3">
          {[
            '리스크는 어느 투자에나 존재합니다. 인덕원삼성의 리모델링도 지연·무산 리스크가 있습니다.',
            '송파구 재건축은 완공 후 "브랜드 신축 아파트"가 되며, 이는 서울에서 대체 불가능한 자산입니다.',
            '가락동 단지들은 현재 가격이 전고점 대비 83~85% 수준으로 상대적 저평가 구간에 있습니다.',
            '무리한 레버리지 없이, 이미 보유한 17억 자기자본 내에서 진입 가능한 단지가 있습니다.',
            '"이 가격 이하라면" 조건부 검토 — 충동 매수 아닌 논리적 기준을 세우고 접근하는 것이 핵심입니다.',
          ].map((text, i) => (
            <div key={i} className="flex gap-3 items-start">
              <span className="text-green-600 font-bold text-lg flex-shrink-0 leading-5">✓</span>
              <p className="text-sm text-green-800 leading-relaxed">{text}</p>
            </div>
          ))}
        </div>
      </div>

      {/* 아내에게 전하는 논리 */}
      <div className="bg-gradient-to-br from-pink-50 to-purple-50 border border-pink-200 rounded-2xl p-6">
        <h2 className="text-xl font-black text-pink-900 mb-2">💌 아내에게 전하는 논리적 설득 포인트</h2>
        <p className="text-xs text-pink-600 mb-4">"무조건 사자"가 아닌, "이 조건이면 검토할 만하다"는 논리입니다</p>
        <div className="space-y-4">
          {[
            {
              q: '왜 지금이어야 해?',
              a: '전고점 대비 15% 빠진 지금이 2021년 최고가 때보다 훨씬 합리적인 진입가입니다. 재건축 사업이 진행될수록 가격은 올라갑니다.',
            },
            {
              q: '우리가 무리하는 거 아니야?',
              a: '가락동 단지들은 17억 자기자본으로 대출 없이도 진입 가능합니다. 대출이 필요하더라도 3억 이하면 충분히 감당 가능한 수준입니다.',
            },
            {
              q: '재건축이 언제 끝날지도 모르잖아?',
              a: '맞습니다. 하지만 재건축 기간 동안에도 "재건축 단지" 프리미엄으로 시세는 꾸준히 오릅니다. 완공이 목적이 아니라 자산 가치 상승이 목적입니다.',
            },
            {
              q: '아이 학교는?',
              a: '송파구는 강남 3구에 준하는 학군을 보유하고 있습니다. 특히 잠실·방이 생활권은 학원가와 자연환경(올림픽공원)을 모두 갖추고 있습니다.',
            },
            {
              q: '인덕원이 더 편한데...',
              a: '지금은 편하지만, 10년 후 인덕원 리모델링 단지와 송파 재건축 신축 단지의 자산가치 격차는 더 벌어질 가능성이 높습니다. 장기 안목으로 결정하세요.',
            },
          ].map((item) => (
            <div key={item.q} className="bg-white rounded-xl p-4 border border-pink-100">
              <p className="font-bold text-pink-800 text-sm mb-1.5">Q. {item.q}</p>
              <p className="text-sm text-gray-700 leading-relaxed">A. {item.a}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Final CTA */}
      <div className="bg-blue-600 rounded-2xl p-6 text-white text-center">
        <h2 className="text-xl font-black mb-2">결론: 검토 가능한 조건</h2>
        <p className="text-blue-100 text-sm mb-4">
          무조건 사야 한다는 것이 아닙니다. 아래 조건을 모두 충족하면 진지하게 검토할 만합니다.
        </p>
        <div className="grid sm:grid-cols-3 gap-3 mb-4">
          {[
            '현재 보유 단지를 12억 이상으로 매도 가능한 경우',
            '총 대출이 3~4억 이하로 DSR 범위 내에서 가능한 경우',
            '최소 5~7년 이상 보유 의지가 있는 경우',
          ].map((cond, i) => (
            <div key={i} className="bg-white/15 rounded-xl p-3 text-sm text-white">
              <span className="text-blue-200 font-bold">{i + 1}.</span> {cond}
            </div>
          ))}
        </div>
        <p className="text-xs text-blue-200">
          * 위 조건을 충족하더라도 최종 결정은 전문가(공인중개사, 세무사, 금융 전문가) 상담 후 본인 책임하에 진행하세요.
        </p>
      </div>

      {/* Navigation */}
      <div className="flex gap-3">
        <Link href="/simulation" className="flex-1 text-center bg-gray-100 text-gray-700 rounded-xl py-3 font-bold hover:bg-gray-200 transition-colors">
          ← 자금 시뮬레이션
        </Link>
        <Link href="/" className="flex-1 text-center bg-blue-600 text-white rounded-xl py-3 font-bold hover:bg-blue-700 transition-colors">
          대시보드로 →
        </Link>
      </div>
    </div>
  );
}
