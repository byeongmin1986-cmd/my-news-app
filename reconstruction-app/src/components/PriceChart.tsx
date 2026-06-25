'use client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer } from 'recharts';
import { PricePoint } from '@/data/types';

interface Props {
  data: PricePoint[];
  highestPrice?: number;
  priceKey?: 'price24py' | 'price27py' | 'price32py';
}

function formatTick(manwon: number): string {
  if (manwon >= 10000) return `${(manwon / 10000).toFixed(0)}억`;
  return `${(manwon / 1000).toFixed(0)}천`;
}

function formatTooltipValue(manwon: number): string {
  const eok = Math.floor(manwon / 10000);
  const rest = manwon % 10000;
  if (rest === 0) return `${eok}억원`;
  return `${eok}억 ${rest.toLocaleString()}만원`;
}

function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{value: number}>; label?: string }) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-gray-900 text-white text-xs rounded-lg px-3 py-2 shadow-lg">
        <p className="text-gray-300 mb-0.5">{label}</p>
        <p className="font-bold">{formatTooltipValue(payload[0].value)}</p>
        <p className="text-gray-400 text-xs mt-0.5">* 추정치 — 재확인 필요</p>
      </div>
    );
  }
  return null;
}

export default function PriceChart({ data, highestPrice, priceKey = 'price24py' }: Props) {
  const formatted = data.map((d) => ({
    ...d,
    date: d.date.replace('-01', '.01').replace('-04', '.04').replace('-07', '.07').replace('-10', '.10'),
  }));

  const min = Math.min(...data.map((d) => (d[priceKey] ?? d.price24py) as number));
  const max = Math.max(...data.map((d) => (d[priceKey] ?? d.price24py) as number));
  const padding = (max - min) * 0.15;

  return (
    <div style={{ height: 220 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={formatted} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 10, fill: '#94a3b8' }}
            interval={2}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={[min - padding, max + padding]}
            tickFormatter={formatTick}
            tick={{ fontSize: 10, fill: '#94a3b8' }}
            axisLine={false}
            tickLine={false}
            width={40}
          />
          <Tooltip content={<CustomTooltip />} />
          {highestPrice && (
            <ReferenceLine
              y={highestPrice}
              stroke="#ef4444"
              strokeDasharray="4 2"
              label={{ value: '최고가', position: 'insideTopRight', fontSize: 9, fill: '#ef4444' }}
            />
          )}
          <Line
            type="monotone"
            dataKey={priceKey}
            stroke="#3b82f6"
            strokeWidth={2.5}
            dot={{ r: 3, fill: '#3b82f6' }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
