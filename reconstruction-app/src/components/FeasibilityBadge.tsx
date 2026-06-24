interface Props {
  status: '가능' | '주의' | '무리' | '불가';
  className?: string;
}

const statusStyle: Record<string, string> = {
  가능: 'bg-green-100 text-green-700 border-green-300',
  주의: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  무리: 'bg-orange-100 text-orange-700 border-orange-300',
  불가: 'bg-red-100 text-red-700 border-red-300',
};

const statusIcon: Record<string, string> = {
  가능: '✅',
  주의: '⚠️',
  무리: '🔶',
  불가: '❌',
};

export default function FeasibilityBadge({ status, className = '' }: Props) {
  return (
    <span
      className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-bold border ${statusStyle[status]} ${className}`}
    >
      {statusIcon[status]} {status}
    </span>
  );
}
