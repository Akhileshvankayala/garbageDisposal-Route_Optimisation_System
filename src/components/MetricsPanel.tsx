import { Route, TrendingUp, Trash2 } from 'lucide-react';

interface MetricsPanelProps {
  totalDistance: number;
  wasteCollected: number;
  disposalTrips: number;
  unit: string;
  isVisible: boolean;
}

export default function MetricsPanel({
  totalDistance,
  wasteCollected,
  disposalTrips,
  unit,
  isVisible,
}: MetricsPanelProps) {
  if (!isVisible) return null;

  return (
    <div className="absolute top-6 right-6 bg-white border-2 border-gray-300 rounded-lg shadow-xl p-6 w-72">
      <h3 className="text-lg font-bold text-gray-900 mb-4">Route Metrics</h3>

      <div className="space-y-4">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Route className="text-blue-600" size={20} />
          </div>
          <div>
            <div className="text-sm text-gray-500">Total Distance</div>
            <div className="text-xl font-bold text-gray-900">
              {totalDistance.toFixed(1)} m
            </div>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="p-2 bg-green-100 rounded-lg">
            <TrendingUp className="text-green-600" size={20} />
          </div>
          <div>
            <div className="text-sm text-gray-500">Waste Collected</div>
            <div className="text-xl font-bold text-gray-900">
              {wasteCollected.toFixed(1)} kg
            </div>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="p-2 bg-orange-100 rounded-lg">
            <Trash2 className="text-orange-600" size={20} />
          </div>
          <div>
            <div className="text-sm text-gray-500">Disposal Trips</div>
            <div className="text-xl font-bold text-gray-900">{disposalTrips}</div>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="text-xs text-gray-500 text-center">
          Real-time route data
        </div>
      </div>
    </div>
  );
}
