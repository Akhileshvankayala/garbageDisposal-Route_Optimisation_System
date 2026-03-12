import React, { useState, useEffect } from 'react';
import { CheckCircle, AlertCircle, Clock, Trash2, Plus } from 'lucide-react';

interface RouteInfo {
  route_id: number;
  vehicle_id: number;
  route_status: string;
  start_time: string;
  end_time: string | null;
}

interface StopInfo {
  stop_id: number;
  hospital_id: number;
  hospital_name: string;
  stop_sequence: number;
  arrival_time: string | null;
  departure_time: string | null;
  waste_collected_kg: number;
}

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
  collections: unknown[];
}

interface Props {
  driverId: number | null;
}

const DriverDashboard: React.FC<Props> = ({ driverId }) => {
  const [assignedRoutes, setAssignedRoutes] = useState<RouteInfo[]>([]);
  const [currentRoute, setCurrentRoute] = useState<RouteInfo | null>(null);
  const [routeStops, setRouteStops] = useState<RouteStop[]>([]);
  const [selectedStop, setSelectedStop] = useState<RouteStop | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmingAction, setConfirmingAction] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!driverId) return;
    fetchAssignedRoutes();
  }, [driverId]);

  const fetchAssignedRoutes = async () => {
    if (!driverId) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/drivers/${driverId}/assigned-routes`);
      if (!response.ok) throw new Error('Failed to fetch assigned routes');
      const data = await response.json();
      setAssignedRoutes(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const fetchCurrentRoute = async () => {
    if (!driverId) return;
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/drivers/${driverId}/current-route`);
      if (!response.ok) throw new Error('No active route');
      const data = await response.json();
      setCurrentRoute(data);
      await fetchRouteStops(data.route_id);
    } catch (err) {
      setCurrentRoute(null);
      setRouteStops([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchRouteStops = async (routeId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/routes/${routeId}/stops`);
      if (!response.ok) throw new Error('Failed to fetch stops');
      const data = await response.json();
      setRouteStops(data);
    } catch (err) {
      console.error('Error fetching stops:', err);
    }
  };

  const confirmArrival = async (routeId: number, stopId: number) => {
    try {
      setConfirmingAction(`arrival-${stopId}`);
      const response = await fetch(
        `http://localhost:8000/api/drivers/routes/${routeId}/stops/${stopId}/confirm-arrival`,
        { method: 'POST' }
      );
      if (!response.ok) throw new Error('Failed to confirm arrival');
      setSuccessMessage('Arrival confirmed!');
      setTimeout(() => setSuccessMessage(null), 2000);
      await fetchCurrentRoute();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error confirming arrival');
    } finally {
      setConfirmingAction(null);
    }
  };

  const confirmDeparture = async (routeId: number, stopId: number) => {
    try {
      setConfirmingAction(`departure-${stopId}`);
      const response = await fetch(
        `http://localhost:8000/api/drivers/routes/${routeId}/stops/${stopId}/confirm-departure`,
        { method: 'POST' }
      );
      if (!response.ok) throw new Error('Failed to confirm departure');
      setSuccessMessage('Departure confirmed!');
      setTimeout(() => setSuccessMessage(null), 2000);
      await fetchCurrentRoute();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error confirming departure');
    } finally {
      setConfirmingAction(null);
    }
  };

  const recordCollection = async (routeId: number, stopId: number, amount: number, staffName: string, notes: string) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/drivers/routes/${routeId}/stops/${stopId}/record-collection`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            bin_id: 1, // In a real app, would select from available bins
            amount_kg: amount,
            staff_name: staffName,
            notes: notes
          })
        }
      );
      if (!response.ok) throw new Error('Failed to record collection');
      setSuccessMessage('Collection recorded!');
      setTimeout(() => setSuccessMessage(null), 2000);
      setSelectedStop(null);
      await fetchCurrentRoute();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error recording collection');
    }
  };

  const formatDateTime = (isoString: string | null): string => {
    if (!isoString) return 'Pending';
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString();
    } catch {
      return isoString;
    }
  };

  if (!driverId) {
    return (
      <div className="p-6 bg-white rounded-lg shadow">
        <p className="text-gray-500">No driver selected</p>
      </div>
    );
  }

  return (
    <div className="w-full space-y-4">
      {/* Success Message */}
      {successMessage && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center">
          <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
          <span className="text-green-800">{successMessage}</span>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center">
          <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
          <span className="text-red-800">{error}</span>
        </div>
      )}

      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-green-700 p-6 text-white rounded-lg shadow-lg">
        <h2 className="text-2xl font-bold mb-2">Driver Dashboard</h2>
        <p className="text-green-100">Driver ID: {driverId}</p>
        <button
          onClick={fetchCurrentRoute}
          disabled={loading}
          className="mt-4 bg-white text-green-700 hover:bg-green-50 font-semibold py-2 px-4 rounded transition disabled:opacity-50"
        >
          {loading ? 'Loading...' : 'Refresh Current Route'}
        </button>
      </div>

      {/* Current Route */}
      {currentRoute && (
        <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Clock className="h-6 w-6 text-yellow-600 mr-2" />
            <h3 className="text-lg font-bold text-yellow-900">Active Route</h3>
          </div>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-sm text-yellow-700">Route ID</p>
              <p className="text-2xl font-bold text-yellow-900">#{currentRoute.route_id}</p>
            </div>
            <div>
              <p className="text-sm text-yellow-700">Vehicle ID</p>
              <p className="text-2xl font-bold text-yellow-900">#{currentRoute.vehicle_id}</p>
            </div>
          </div>

          {/* Route Stops */}
          <div className="space-y-3">
            <h4 className="font-semibold text-yellow-900">Stops</h4>
            {routeStops.length === 0 ? (
              <p className="text-yellow-700">No stops loaded</p>
            ) : (
              routeStops.map((stop) => (
                <div key={stop.stop_id} className="bg-white border border-yellow-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h5 className="font-semibold text-gray-900">
                        Stop {stop.stop_sequence}: {stop.hospital_name}
                      </h5>
                      <p className="text-sm text-gray-600">Hospital ID: {stop.hospital_id}</p>
                    </div>
                    <div className="flex gap-2">
                      {!stop.arrival_time && (
                        <button
                          onClick={() => confirmArrival(currentRoute.route_id, stop.stop_id)}
                          disabled={confirmingAction === `arrival-${stop.stop_id}`}
                          className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-1 px-2 rounded text-xs disabled:opacity-50"
                        >
                          {confirmingAction === `arrival-${stop.stop_id}` ? 'Confirming...' : 'Confirm Arrival'}
                        </button>
                      )}
                      {stop.arrival_time && !stop.departure_time && (
                        <button
                          onClick={() => confirmDeparture(currentRoute.route_id, stop.stop_id)}
                          disabled={confirmingAction === `departure-${stop.stop_id}`}
                          className="bg-orange-500 hover:bg-orange-600 text-white font-bold py-1 px-2 rounded text-xs disabled:opacity-50"
                        >
                          {confirmingAction === `departure-${stop.stop_id}` ? 'Confirming...' : 'Confirm Departure'}
                        </button>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 mb-3 text-sm">
                    <div className="bg-blue-50 p-2 rounded">
                      <p className="text-xs text-blue-600">Arrival</p>
                      <p className="font-medium text-blue-900">{formatDateTime(stop.arrival_time)}</p>
                    </div>
                    <div className="bg-blue-50 p-2 rounded">
                      <p className="text-xs text-blue-600">Departure</p>
                      <p className="font-medium text-blue-900">{formatDateTime(stop.departure_time)}</p>
                    </div>
                  </div>

                  {stop.arrival_time && !stop.departure_time && (
                    <button
                      onClick={() => setSelectedStop(stop)}
                      className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-3 rounded flex items-center justify-center gap-2 text-sm"
                    >
                      <Plus className="h-4 w-4" />
                      Record Waste Collection
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {!currentRoute && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
          <p className="text-gray-600 mb-4">No active route</p>
          <button
            onClick={fetchCurrentRoute}
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
          >
            Load Current Route
          </button>
        </div>
      )}

      {/* Assigned Routes */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Assigned Routes ({assignedRoutes.length})</h3>
        <div className="space-y-2">
          {assignedRoutes.map((route) => (
            <div key={route.route_id} className="flex items-center justify-between p-3 bg-gray-50 rounded border">
              <div>
                <p className="font-semibold text-gray-900">Route #{route.route_id}</p>
                <p className="text-sm text-gray-600">Vehicle: {route.vehicle_id}</p>
              </div>
              <div className="text-right">
                <p className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                  route.route_status === 'completed' ? 'bg-green-100 text-green-800' :
                  route.route_status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {route.route_status}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Collection Recording Modal */}
      {selectedStop && currentRoute && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full">
            <div className="flex items-center mb-4">
              <Trash2 className="h-6 w-6 text-purple-600 mr-2" />
              <h3 className="text-lg font-bold text-gray-900">Record Waste Collection</h3>
            </div>

            <div className="space-y-4 mb-6">
              <div>
                <p className="font-semibold text-gray-900">{selectedStop.hospital_name}</p>
                <p className="text-sm text-gray-600">Stop {selectedStop.stop_sequence}</p>
              </div>

              <CollectionForm
                onSubmit={(amount, staffName, notes) => {
                  recordCollection(currentRoute.route_id, selectedStop.stop_id, amount, staffName, notes);
                }}
                onCancel={() => setSelectedStop(null)}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

interface CollectionFormProps {
  onSubmit: (amount: number, staffName: string, notes: string) => void;
  onCancel: () => void;
}

const CollectionForm: React.FC<CollectionFormProps> = ({ onSubmit, onCancel }) => {
  const [amount, setAmount] = useState<number>(0);
  const [staffName, setStaffName] = useState<string>('');
  const [notes, setNotes] = useState<string>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (amount <= 0) {
      alert('Please enter a valid amount');
      return;
    }
    onSubmit(amount, staffName, notes);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Amount (kg)</label>
        <input
          type="number"
          step="0.1"
          min="0"
          value={amount}
          onChange={(e) => setAmount(parseFloat(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Staff Name</label>
        <input
          type="text"
          value={staffName}
          onChange={(e) => setStaffName(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          placeholder="Enter staff name"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          placeholder="Add any notes..."
          rows={2}
        />
      </div>

      <div className="flex gap-2">
        <button
          type="submit"
          className="flex-1 bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded"
        >
          Record Collection
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded"
        >
          Cancel
        </button>
      </div>
    </form>
  );
};

export default DriverDashboard;
