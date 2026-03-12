import React, { useState, useEffect } from 'react';
import { Clock, MapPin, Truck, Weight, AlertCircle } from 'lucide-react';

interface RouteStop {
  stop_id: number;
  route_id: number;
  hospital_id: number;
  hospital_name: string;
  stop_sequence: number;
  arrival_time: string | null;
  departure_time: string | null;
  waste_collected_kg: number;
  vehicle_load_at_stop_kg: number;
  collections: WasteCollection[];
}

interface WasteCollection {
  collection_id: number;
  stop_id: number;
  bin_id: number;
  amount_kg: number;
  collection_time: string;
  staff_name: string | null;
  notes: string | null;
}

interface RouteDetail {
  route_id: number;
  vehicle_id: number;
  driver_id: number;
  route_status: string;
  start_location_x: number;
  start_location_y: number;
  end_location_x: number | null;
  end_location_y: number | null;
  total_distance_m: number;
  total_waste_collected_kg: number;
  num_disposal_trips: number;
  start_time: string;
  end_time: string | null;
  stops: RouteStop[];
  created_at: string;
  updated_at: string;
}

interface Props {
  routeId: number | null;
  onClose?: () => void;
}

const RouteDetailPanel: React.FC<Props> = ({ routeId, onClose }) => {
  const [route, setRoute] = useState<RouteDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!routeId) return;

    const fetchRoute = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`http://localhost:8000/api/routes/${routeId}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch route: ${response.statusText}`);
        }
        const data = await response.json();
        setRoute(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Error fetching route:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRoute();
  }, [routeId]);

  const formatDateTime = (isoString: string | null): string => {
    if (!isoString) return 'N/A';
    try {
      const date = new Date(isoString);
      return date.toLocaleString();
    } catch {
      return isoString;
    }
  };

  const calculateDuration = (
    arrivalTime: string | null,
    departureTime: string | null
  ): string => {
    if (!arrivalTime || !departureTime) return 'N/A';
    try {
      const arrival = new Date(arrivalTime).getTime();
      const departure = new Date(departureTime).getTime();
      const minutes = Math.round((departure - arrival) / 60000);
      return `${minutes} min`;
    } catch {
      return 'N/A';
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'planned':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'cancelled':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="p-6 bg-white rounded-lg shadow">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-2 text-gray-600">Loading route details...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 rounded-lg shadow border border-red-200">
        <div className="flex items-start">
          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-red-900">Error</h3>
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!route) {
    return (
      <div className="p-6 bg-white rounded-lg shadow">
        <p className="text-gray-500">No route selected</p>
      </div>
    );
  }

  return (
    <div className="w-full bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-6 text-white">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-bold">Route #{route.route_id}</h2>
            <p className="text-blue-100">Vehicle {route.vehicle_id} - Driver {route.driver_id}</p>
          </div>
          <div className={`px-3 py-1 rounded-full border text-sm font-semibold ${getStatusColor(route.route_status)}`}>
            {route.route_status.replace('_', ' ').toUpperCase()}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6 space-y-6">
        {/* Route Metrics */}
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center text-gray-600 mb-2">
              <MapPin className="h-4 w-4 mr-2" />
              <span className="text-sm">Distance</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{route.total_distance_m.toFixed(1)}m</p>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center text-gray-600 mb-2">
              <Weight className="h-4 w-4 mr-2" />
              <span className="text-sm">Waste Collected</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{route.total_waste_collected_kg.toFixed(1)}kg</p>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center text-gray-600 mb-2">
              <Truck className="h-4 w-4 mr-2" />
              <span className="text-sm">Disposal Trips</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{route.num_disposal_trips}</p>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center text-gray-600 mb-2">
              <Clock className="h-4 w-4 mr-2" />
              <span className="text-sm">Duration</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">
              {route.end_time
                ? `${Math.round((new Date(route.end_time).getTime() - new Date(route.start_time).getTime()) / 60000)} min`
                : 'Active'}
            </p>
          </div>
        </div>

        {/* Time Information */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-3">Timeline</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-blue-700">Started:</span>
              <span className="text-gray-900 font-medium">{formatDateTime(route.start_time)}</span>
            </div>
            {route.end_time && (
              <div className="flex justify-between">
                <span className="text-blue-700">Completed:</span>
                <span className="text-gray-900 font-medium">{formatDateTime(route.end_time)}</span>
              </div>
            )}
          </div>
        </div>

        {/* Stops */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Route Stops ({route.stops.length})</h3>
          <div className="space-y-3">
            {route.stops.map((stop) => (
              <div key={stop.stop_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-gray-900">
                      Stop {stop.stop_sequence}: {stop.hospital_name}
                    </h4>
                    <p className="text-sm text-gray-600">Hospital ID: {stop.hospital_id}</p>
                  </div>
                  <div className="bg-gray-100 px-2 py-1 rounded text-sm font-medium text-gray-700">
                    #{stop.stop_id}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 mb-3">
                  <div className="bg-gray-50 p-2 rounded">
                    <p className="text-xs text-gray-600">Arrival</p>
                    <p className="text-sm font-medium text-gray-900">
                      {formatDateTime(stop.arrival_time)}
                    </p>
                  </div>
                  <div className="bg-gray-50 p-2 rounded">
                    <p className="text-xs text-gray-600">Departure</p>
                    <p className="text-sm font-medium text-gray-900">
                      {formatDateTime(stop.departure_time)}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 mb-3">
                  <div className="bg-blue-50 p-2 rounded">
                    <p className="text-xs text-blue-600">Waste Collected</p>
                    <p className="text-sm font-bold text-blue-900">{stop.waste_collected_kg.toFixed(1)}kg</p>
                  </div>
                  <div className="bg-green-50 p-2 rounded">
                    <p className="text-xs text-green-600">Vehicle Load</p>
                    <p className="text-sm font-bold text-green-900">{stop.vehicle_load_at_stop_kg.toFixed(1)}kg</p>
                  </div>
                </div>

                <div className="text-xs text-gray-600 mb-2">
                  Stop Duration: {calculateDuration(stop.arrival_time, stop.departure_time)}
                </div>

                {/* Collections */}
                {stop.collections.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs font-semibold text-gray-700 mb-2">Collections ({stop.collections.length})</p>
                    <div className="space-y-1">
                      {stop.collections.map((collection) => (
                        <div key={collection.collection_id} className="text-xs bg-yellow-50 p-2 rounded border border-yellow-100">
                          <div className="flex justify-between">
                            <span className="font-medium text-yellow-900">{collection.amount_kg}kg</span>
                            <span className="text-yellow-700">{collection.staff_name || 'Unknown Staff'}</span>
                          </div>
                          {collection.notes && (
                            <p className="text-yellow-700 mt-1 italic">Note: {collection.notes}</p>
                          )}
                          <p className="text-yellow-600">{formatDateTime(collection.collection_time)}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Close Button */}
        {onClose && (
          <div className="pt-4 border-t">
            <button
              onClick={onClose}
              className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-2 px-4 rounded transition"
            >
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default RouteDetailPanel;
