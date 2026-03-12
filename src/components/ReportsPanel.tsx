import React, { useState, useEffect } from 'react';
import { X, TrendingUp, Trash2, Truck, Activity, Calendar } from 'lucide-react';

interface HospitalWaste {
  hospital_id: number;
  hospital_name: string;
  current_waste_kg: number;
  max_capacity: number;
  fill_percentage: number;
  last_updated: string;
}

interface RouteHistory {
  route_id: number;
  vehicle_id: number;
  driver_id: number;
  start_time: string;
  end_time: string | null;
  total_distance_m: number;
  total_waste_collected_kg: number;
  disposal_trips: number;
  hospitals_visited: number;
  route_status: string;
}

interface SummaryData {
  hospitals: {
    total: number;
    active: number;
    total_waste_kg: number;
    average_fill_percentage: number;
  };
  vehicles: {
    total: number;
    on_route: number;
    idle: number;
  };
  routes_today: {
    completed: number;
    pending: number;
    total_distance_m: number;
  };
}

interface ReportsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ReportsPanel({ isOpen, onClose }: ReportsPanelProps) {
  const [activeTab, setActiveTab] = useState<'waste' | 'routes' | 'summary'>('summary');
  const [wasteData, setWasteData] = useState<HospitalWaste[]>([]);
  const [routeData, setRouteData] = useState<RouteHistory[]>([]);
  const [summaryData, setSummaryData] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(1);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchAllData();
      // Removed auto-refresh - only manual refresh via button
    }
  }, [isOpen, days]);

  const fetchAllData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch all three reports in parallel
      const [wasteRes, routesRes, summaryRes] = await Promise.all([
        fetch('http://localhost:8000/api/reports/waste'),
        fetch(`http://localhost:8000/api/reports/routes?days=${days}`),
        fetch('http://localhost:8000/api/reports/summary'),
      ]);

      if (!wasteRes.ok || !routesRes.ok || !summaryRes.ok) {
        throw new Error('Failed to fetch reports');
      }

      const wasteJson = await wasteRes.json();
      const routesJson = await routesRes.json();
      const summaryJson = await summaryRes.json();

      setWasteData(wasteJson.hospitals || []);
      setRouteData(routesJson.routes || []);
      setSummaryData(summaryJson);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch reports');
      console.error('Error fetching reports:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between border-b p-6">
          <div className="flex items-center gap-3">
            <Activity className="h-6 w-6 text-blue-600" />
            <h2 className="text-2xl font-bold text-gray-900">System Reports</h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => { setRefreshing(true); fetchAllData().then(() => setRefreshing(false)); }}
              disabled={refreshing || loading}
              className={`px-4 py-2 rounded-lg transition font-medium flex items-center gap-2 ${refreshing || loading ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}
              title="Refresh data"
            >
              <Activity className={`h-5 w-5 ${refreshing ? 'animate-spin' : ''}`} />
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition"
            >
              <X className="h-6 w-6 text-gray-600" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b bg-gray-50">
          <button
            onClick={() => setActiveTab('summary')}
            className={`flex-1 px-6 py-4 font-medium transition ${
              activeTab === 'summary'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            System Overview
          </button>
          <button
            onClick={() => setActiveTab('waste')}
            className={`flex-1 px-6 py-4 font-medium transition ${
              activeTab === 'waste'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Waste Status
          </button>
          <button
            onClick={() => setActiveTab('routes')}
            className={`flex-1 px-6 py-4 font-medium transition ${
              activeTab === 'routes'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Route History
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto flex-1 p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="animate-spin mb-4">
                  <Activity className="h-8 w-8 text-blue-600" />
                </div>
                <p className="text-gray-600">Loading reports...</p>
              </div>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800">Error: {error}</p>
              <button
                onClick={fetchAllData}
                className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Retry
              </button>
            </div>
          ) : (
            <>
              {/* Summary Tab */}
              {activeTab === 'summary' && summaryData && (
                <div className="space-y-6">
                  <div className="grid grid-cols-3 gap-4">
                    {/* Hospitals Card */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="font-semibold text-gray-900">Hospitals</h3>
                        <div className="p-2 bg-blue-100 rounded-lg">
                          <TrendingUp className="h-5 w-5 text-blue-600" />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div>
                          <p className="text-sm text-gray-600">Total</p>
                          <p className="text-2xl font-bold text-gray-900">{summaryData.hospitals.total}</p>
                        </div>
                        <div className="pt-2 border-t">
                          <p className="text-sm text-gray-600">Active</p>
                          <p className="text-xl font-bold text-blue-600">{summaryData.hospitals.active}</p>
                        </div>
                        <div className="pt-2 border-t">
                          <p className="text-sm text-gray-600">Avg Fill %</p>
                          <p className="text-xl font-bold text-gray-900">
                            {summaryData.hospitals.average_fill_percentage.toFixed(1)}%
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Waste Card */}
                    <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="font-semibold text-gray-900">System Waste</h3>
                        <div className="p-2 bg-green-100 rounded-lg">
                          <Trash2 className="h-5 w-5 text-green-600" />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div>
                          <p className="text-sm text-gray-600">Total Waste</p>
                          <p className="text-2xl font-bold text-gray-900">
                            {summaryData.hospitals.total_waste_kg.toFixed(1)} kg
                          </p>
                        </div>
                        <div className="pt-2 border-t">
                          <p className="text-sm text-gray-600">Avg per Hospital</p>
                          <p className="text-lg font-bold text-green-600">
                            {(summaryData.hospitals.total_waste_kg / Math.max(summaryData.hospitals.total, 1)).toFixed(1)} kg
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Vehicles Card */}
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="font-semibold text-gray-900">Vehicles</h3>
                        <div className="p-2 bg-purple-100 rounded-lg">
                          <Truck className="h-5 w-5 text-purple-600" />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div>
                          <p className="text-sm text-gray-600">Total</p>
                          <p className="text-2xl font-bold text-gray-900">{summaryData.vehicles.total}</p>
                        </div>
                        <div className="pt-2 border-t">
                          <p className="text-sm text-gray-600">On Route</p>
                          <p className="text-xl font-bold text-purple-600">{summaryData.vehicles.on_route}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Idle</p>
                          <p className="text-xl font-bold text-gray-900">{summaryData.vehicles.idle}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Routes Today */}
                  <div className="bg-gray-50 border rounded-lg p-6">
                    <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <Calendar className="h-5 w-5" />
                      Today's Routes
                    </h3>
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <p className="text-sm text-gray-600">Completed</p>
                        <p className="text-2xl font-bold text-green-600">{summaryData.routes_today.completed}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Pending</p>
                        <p className="text-2xl font-bold text-yellow-600">{summaryData.routes_today.pending}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Total Distance</p>
                        <p className="text-2xl font-bold text-blue-600">{summaryData.routes_today.total_distance_m.toFixed(0)} m</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Waste Tab */}
              {activeTab === 'waste' && (
                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-900">Current Waste Status by Hospital</h3>
                  {wasteData.length === 0 ? (
                    <p className="text-gray-600">No waste data available</p>
                  ) : (
                    <div className="space-y-3">
                      {wasteData.map((hospital) => (
                        <div key={hospital.hospital_id} className="border rounded-lg p-4 hover:bg-gray-50 transition">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-semibold text-gray-900">{hospital.hospital_name}</h4>
                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                              hospital.fill_percentage > 80
                                ? 'bg-red-100 text-red-800'
                                : hospital.fill_percentage > 60
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-green-100 text-green-800'
                            }`}>
                              {hospital.fill_percentage.toFixed(1)}%
                            </span>
                          </div>
                          <div className="flex items-center gap-4">
                            <div className="flex-1">
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                  className={`h-2 rounded-full transition ${
                                    hospital.fill_percentage > 80
                                      ? 'bg-red-500'
                                      : hospital.fill_percentage > 60
                                      ? 'bg-yellow-500'
                                      : 'bg-green-500'
                                  }`}
                                  style={{ width: `${Math.min(hospital.fill_percentage, 100)}%` }}
                                />
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="text-sm font-medium text-gray-900">
                                {hospital.current_waste_kg.toFixed(1)} / {hospital.max_capacity.toFixed(1)} kg
                              </p>
                            </div>
                          </div>
                          <p className="text-xs text-gray-500 mt-2">
                            Updated: {new Date(hospital.last_updated).toLocaleString()}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Routes Tab */}
              {activeTab === 'routes' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-gray-900">Route History</h3>
                    <select
                      value={days}
                      onChange={(e) => setDays(parseInt(e.target.value))}
                      className="px-3 py-1 border rounded text-sm"
                    >
                      <option value={1}>Last 24 hours</option>
                      <option value={7}>Last 7 days</option>
                      <option value={30}>Last 30 days</option>
                    </select>
                  </div>
                  {routeData.length === 0 ? (
                    <p className="text-gray-600">No routes in selected period</p>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-100 border-b">
                          <tr>
                            <th className="px-4 py-2 text-left font-semibold text-gray-900">Route ID</th>
                            <th className="px-4 py-2 text-left font-semibold text-gray-900">Vehicle</th>
                            <th className="px-4 py-2 text-left font-semibold text-gray-900">Start Time</th>
                            <th className="px-4 py-2 text-left font-semibold text-gray-900">Status</th>
                            <th className="px-4 py-2 text-right font-semibold text-gray-900">Distance (m)</th>
                            <th className="px-4 py-2 text-right font-semibold text-gray-900">Waste (kg)</th>
                            <th className="px-4 py-2 text-right font-semibold text-gray-900">Hospitals</th>
                            <th className="px-4 py-2 text-right font-semibold text-gray-900">Disposals</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y">
                          {routeData.map((route) => (
                            <tr key={route.route_id} className="hover:bg-gray-50 transition">
                              <td className="px-4 py-3 font-medium text-gray-900">#{route.route_id}</td>
                              <td className="px-4 py-3 text-gray-700">Truck-{route.vehicle_id.toString().padStart(2, '0')}</td>
                              <td className="px-4 py-3 text-gray-700">
                                {new Date(route.start_time).toLocaleString()}
                              </td>
                              <td className="px-4 py-3">
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                  route.route_status === 'completed'
                                    ? 'bg-green-100 text-green-800'
                                    : route.route_status === 'in_progress'
                                    ? 'bg-blue-100 text-blue-800'
                                    : 'bg-gray-100 text-gray-800'
                                }`}>
                                  {route.route_status === 'in_progress' ? 'In Progress' : 
                                   route.route_status === 'completed' ? 'Completed' : 'Pending'}
                                </span>
                              </td>
                              <td className="px-4 py-3 text-right font-medium text-gray-900">
                                {route.total_distance_m.toFixed(0)}
                              </td>
                              <td className="px-4 py-3 text-right font-medium text-gray-900">
                                {route.total_waste_collected_kg.toFixed(1)}
                              </td>
                              <td className="px-4 py-3 text-right text-gray-700">
                                {route.hospitals_visited}
                              </td>
                              <td className="px-4 py-3 text-right text-gray-700">
                                {route.disposal_trips}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="border-t bg-gray-50 px-6 py-4 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
