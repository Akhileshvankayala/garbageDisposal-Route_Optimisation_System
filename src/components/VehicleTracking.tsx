import React, { useState, useEffect } from 'react';
import { AlertCircle, MapPin, Zap, Wrench, Activity } from 'lucide-react';

interface VehicleTracking {
  vehicle_id: number;
  vehicle_name: string;
  status: string;
  current_location_x: number;
  current_location_y: number;
  current_load_kg: number;
  capacity_kg: number;
  load_percentage: number;
  last_maintenance: string | null;
  current_route_id: number | null;
  current_route_status: string | null;
}

interface Props {
  vehicleId: number | null;
  onVehicleSelect?: (vehicleId: number) => void;
}

const VehicleTracking: React.FC<Props> = ({ vehicleId, onVehicleSelect }) => {
  const [vehicles, setVehicles] = useState<VehicleTracking[]>([]);
  const [selectedVehicle, setSelectedVehicle] = useState<VehicleTracking | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [updateLocation, setUpdateLocation] = useState(false);
  const [newX, setNewX] = useState(0);
  const [newY, setNewY] = useState(0);

  useEffect(() => {
    fetchVehicles();
    const interval = setInterval(fetchVehicles, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (vehicleId && vehicles.length > 0) {
      const vehicle = vehicles.find(v => v.vehicle_id === vehicleId);
      if (vehicle) {
        setSelectedVehicle(vehicle);
      }
    }
  }, [vehicleId, vehicles]);

  const fetchVehicles = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/vehicles');
      if (!response.ok) throw new Error('Failed to fetch vehicles');
      const data = await response.json();
      setVehicles(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateLocation = async (vId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/vehicles/${vId}/location`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ x: newX, y: newY })
      });
      if (!response.ok) throw new Error('Failed to update location');
      setUpdateLocation(false);
      await fetchVehicles();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error updating location');
    }
  };

  const getStatusColor = (status: string): { bg: string; text: string; dot: string } => {
    switch (status) {
      case 'idle':
        return { bg: 'bg-green-100', text: 'text-green-800', dot: 'bg-green-500' };
      case 'on_route':
        return { bg: 'bg-blue-100', text: 'text-blue-800', dot: 'bg-blue-500' };
      case 'at_disposal':
        return { bg: 'bg-orange-100', text: 'text-orange-800', dot: 'bg-orange-500' };
      case 'maintenance':
        return { bg: 'bg-red-100', text: 'text-red-800', dot: 'bg-red-500' };
      default:
        return { bg: 'bg-gray-100', text: 'text-gray-800', dot: 'bg-gray-500' };
    }
  };

  const formatDateTime = (isoString: string | null): string => {
    if (!isoString) return 'N/A';
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch {
      return isoString;
    }
  };

  const getLoadColor = (percentage: number): string => {
    if (percentage >= 80) return 'bg-red-500';
    if (percentage >= 60) return 'bg-orange-500';
    if (percentage >= 30) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="w-full space-y-4">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 p-6 text-white rounded-lg shadow-lg">
        <h2 className="text-2xl font-bold mb-2">Vehicle Tracking System</h2>
        <p className="text-purple-100">Real-time GPS location and load monitoring</p>
        <button
          onClick={fetchVehicles}
          disabled={loading}
          className="mt-4 bg-white text-purple-700 hover:bg-purple-50 font-semibold py-2 px-4 rounded transition disabled:opacity-50"
        >
          {loading ? 'Refreshing...' : 'Refresh Data'}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-red-900">Error</h3>
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Vehicle List */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-4">Vehicles ({vehicles.length})</h3>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {vehicles.map((vehicle) => {
                const colors = getStatusColor(vehicle.status);
                const isSelected = selectedVehicle?.vehicle_id === vehicle.vehicle_id;

                return (
                  <div
                    key={vehicle.vehicle_id}
                    onClick={() => {
                      setSelectedVehicle(vehicle);
                      onVehicleSelect?.(vehicle.vehicle_id);
                    }}
                    className={`p-3 rounded-lg cursor-pointer transition ${
                      isSelected
                        ? `${colors.bg} border-2 border-purple-500`
                        : 'bg-gray-50 border border-gray-200 hover:border-purple-300'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <div className={`w-3 h-3 rounded-full ${colors.dot}`}></div>
                      <p className="font-semibold text-gray-900">{vehicle.vehicle_name}</p>
                    </div>
                    <p className={`text-xs font-medium ${colors.text} mb-1`}>
                      {vehicle.status.replace('_', ' ').toUpperCase()}
                    </p>
                    <p className="text-xs text-gray-600">
                      Load: {vehicle.current_load_kg.toFixed(1)}/{vehicle.capacity_kg}kg
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Selected Vehicle Details */}
        <div className="lg:col-span-2">
          {selectedVehicle ? (
            <div className="space-y-4">
              {/* Main Card */}
              <div className="bg-white rounded-lg shadow-lg overflow-hidden">
                {/* Header */}
                <div className={`${getStatusColor(selectedVehicle.status).bg} p-6`}>
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-2xl font-bold text-gray-900">
                        {selectedVehicle.vehicle_name}
                      </h3>
                      <p className="text-gray-600">
                        Vehicle ID: {selectedVehicle.vehicle_id}
                      </p>
                    </div>
                    <div className={`px-4 py-2 rounded-full ${getStatusColor(selectedVehicle.status).bg}`}>
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${getStatusColor(selectedVehicle.status).dot}`}></div>
                        <span className={`font-semibold ${getStatusColor(selectedVehicle.status).text}`}>
                          {selectedVehicle.status.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                  {/* Location */}
                  <div className="border-b pb-6">
                    <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                      <MapPin className="h-5 w-5 mr-2 text-blue-600" />
                      Current Location
                    </h4>
                    <div className="bg-blue-50 rounded-lg p-4 mb-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-blue-600 font-medium">X Coordinate</p>
                          <p className="text-2xl font-bold text-blue-900">
                            {selectedVehicle.current_location_x.toFixed(2)}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-blue-600 font-medium">Y Coordinate</p>
                          <p className="text-2xl font-bold text-blue-900">
                            {selectedVehicle.current_location_y.toFixed(2)}
                          </p>
                        </div>
                      </div>
                    </div>

                    {updateLocation && (
                      <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            New X Coordinate
                          </label>
                          <input
                            type="number"
                            step="0.1"
                            value={newX}
                            onChange={(e) => setNewX(parseFloat(e.target.value))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            New Y Coordinate
                          </label>
                          <input
                            type="number"
                            step="0.1"
                            value={newY}
                            onChange={(e) => setNewY(parseFloat(e.target.value))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                          />
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleUpdateLocation(selectedVehicle.vehicle_id)}
                            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                          >
                            Update Location
                          </button>
                          <button
                            onClick={() => setUpdateLocation(false)}
                            className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}

                    {!updateLocation && (
                      <button
                        onClick={() => setUpdateLocation(true)}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                      >
                        Update Location
                      </button>
                    )}
                  </div>

                  {/* Load */}
                  <div className="border-b pb-6">
                    <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                      <Zap className="h-5 w-5 mr-2 text-orange-600" />
                      Current Load
                    </h4>
                    <div className="space-y-3">
                      <div className="bg-orange-50 rounded-lg p-4">
                        <div className="flex justify-between mb-2">
                          <span className="font-medium text-gray-900">
                            {selectedVehicle.current_load_kg.toFixed(1)}kg / {selectedVehicle.capacity_kg}kg
                          </span>
                          <span className="font-bold text-orange-900">
                            {selectedVehicle.load_percentage.toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-300 rounded-full h-4 overflow-hidden">
                          <div
                            className={`h-full ${getLoadColor(selectedVehicle.load_percentage)} transition-all duration-500`}
                            style={{ width: `${Math.min(selectedVehicle.load_percentage, 100)}%` }}
                          ></div>
                        </div>
                      </div>

                      {selectedVehicle.load_percentage >= 80 && (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start">
                          <AlertCircle className="h-4 w-4 text-red-600 mr-2 mt-0.5 flex-shrink-0" />
                          <p className="text-sm text-red-800">Vehicle is nearing capacity</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Maintenance */}
                  <div className="border-b pb-6">
                    <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                      <Wrench className="h-5 w-5 mr-2 text-green-600" />
                      Maintenance
                    </h4>
                    <div className="bg-green-50 rounded-lg p-4">
                      <p className="text-sm text-green-600 font-medium">Last Maintenance</p>
                      <p className="text-lg font-semibold text-green-900">
                        {formatDateTime(selectedVehicle.last_maintenance)}
                      </p>
                    </div>
                  </div>

                  {/* Active Route */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                      <Activity className="h-5 w-5 mr-2 text-purple-600" />
                      Active Route
                    </h4>
                    {selectedVehicle.current_route_id ? (
                      <div className="bg-purple-50 rounded-lg p-4">
                        <p className="text-sm text-purple-600 font-medium">Route ID</p>
                        <p className="text-2xl font-bold text-purple-900">
                          #{selectedVehicle.current_route_id}
                        </p>
                        <p className={`text-sm font-medium mt-2 inline-block px-2 py-1 rounded ${
                          selectedVehicle.current_route_status === 'in_progress'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {selectedVehicle.current_route_status || 'Unknown'}
                        </p>
                      </div>
                    ) : (
                      <div className="bg-gray-50 rounded-lg p-4 text-center">
                        <p className="text-gray-600">No active route</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-lg p-8 text-center">
              <p className="text-gray-600 text-lg">Select a vehicle to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VehicleTracking;
