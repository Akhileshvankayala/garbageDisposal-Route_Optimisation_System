import { Scale } from '../types';

interface ScaleIndicatorProps {
  scale: Scale;
}

export default function ScaleIndicator({ scale }: ScaleIndicatorProps) {
  const barWidth = 100;

  return (
    <div className="absolute bottom-6 left-6 bg-white border-2 border-gray-300 rounded-lg px-4 py-3 shadow-md">
      <div className="flex items-center gap-3">
        <div className="relative">
          <div
            className="h-1 bg-gray-800"
            style={{ width: `${barWidth}px` }}
          />
          <div className="absolute -left-1 -top-1 w-0.5 h-3 bg-gray-800" />
          <div className="absolute -right-1 -top-1 w-0.5 h-3 bg-gray-800" />
        </div>
        <span className="text-sm font-medium text-gray-700">
          {barWidth * scale.factor} {scale.unit}
        </span>
      </div>
    </div>
  );
}
