interface Props {
  label: string;
  score: number;
  maxScore?: number;
  invertColor?: boolean;
}

export default function ScoreBar({ label, score, maxScore = 100, invertColor = false }: Props) {
  const pct = Math.round((score / maxScore) * 100);
  const getColor = () => {
    if (invertColor) {
      if (pct <= 30) return 'bg-green-500';
      if (pct <= 60) return 'bg-yellow-500';
      return 'bg-red-500';
    }
    if (pct >= 80) return 'bg-green-500';
    if (pct >= 60) return 'bg-blue-500';
    if (pct >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-1">
        <span className="text-xs text-gray-600">{label}</span>
        <span className="text-xs font-bold text-gray-800">{score}</span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${getColor()}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
