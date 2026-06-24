import { STAGE_LABELS } from '@/data/complexes';

interface Props {
  stageCode: number;
  className?: string;
}

const colorMap: Record<string, string> = {
  gray: 'bg-gray-100 text-gray-600 border-gray-200',
  yellow: 'bg-yellow-50 text-yellow-700 border-yellow-200',
  blue: 'bg-blue-50 text-blue-700 border-blue-200',
  indigo: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  purple: 'bg-purple-50 text-purple-700 border-purple-200',
  green: 'bg-green-50 text-green-700 border-green-200',
};

export default function StageBadge({ stageCode, className = '' }: Props) {
  const { label, color } = STAGE_LABELS[stageCode] ?? STAGE_LABELS[0];
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${colorMap[color]} ${className}`}
    >
      {label}
    </span>
  );
}
