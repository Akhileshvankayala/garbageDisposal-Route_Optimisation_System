import { useState } from 'react';
import { MousePointer, Link, Eye, Trash2, Play } from 'lucide-react';
import { Mode, Scale } from '../types';

interface SidebarProps {
  mode: Mode;
  onModeChange: (mode: Mode) => void;
  scale: Scale;
  onScaleChange: (scale: Scale) => void;
  scales: Scale[];
  onClear: () => void;
  onVisualizeRoute: () => void;
  canVisualizeRoute: boolean;
  onUndo: () => void;
  onRedo: () => void;
  canUndo: boolean;
  canRedo: boolean;
  role: 'guest' | 'admin' | 'staff' | 'driver';
  onLogin: (role: 'admin' | 'staff' | 'driver', password: string) => void;
  onLogout: () => void;
  loginError?: string | null;
  nodes: { id: string; label?: string; type?: string; waste?: number }[];
  onUpdateWaste: (nodeId: string, amount: number) => void;
  onDriverMarkPickupDone: (nodeId: string) => void;
  onViewReports?: () => void;
}

export default function Sidebar({
  mode,
  onModeChange,
  scale,
  onScaleChange,
  scales,
  onClear,
  onVisualizeRoute,
  canVisualizeRoute,
  onUndo,
  onRedo,
  canUndo,
  canRedo,
  role,
  onLogin,
  onLogout,
  loginError,
  nodes,
  onUpdateWaste,
  onDriverMarkPickupDone,
  onViewReports,
}: SidebarProps) {
  const [selectedRole, setSelectedRole] = useState<'admin' | 'staff' | 'driver'>('admin');
  const [password, setPassword] = useState('');
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedDriverNode, setSelectedDriverNode] = useState<string | null>(null);
  return (
    <div className="w-80 bg-white border-r-2 border-gray-200 p-6 flex flex-col h-full">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">MediTrack</h1>
        <p className="text-sm text-gray-500 mt-1">
          Route Visualization Playground
        </p>
        <p className="text-xs text-gray-400 mt-1">Shortcuts: <span className="font-medium">Ctrl+Z</span> Undo, <span className="font-medium">Ctrl+Shift+Z</span> Redo</p>
      </div>

      {/* Role selector and login */}
      <div className="mb-4">
        {role === 'guest' ? (
          <div className="space-y-2">
            <label className="text-xs text-gray-600">Select role</label>
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value as any)}
              className="w-full p-2 border rounded"
            >
              <option value="admin">Admin</option>
              <option value="staff">Staff</option>
              <option value="driver">Collection driver</option>
            </select>

            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              className="w-full p-2 border rounded"
            />

            <div className="flex gap-2">
              <button
                onClick={() => onLogin(selectedRole, password)}
                className="flex-1 p-2 bg-blue-600 text-white rounded"
              >
                Login
              </button>
            </div>

            {loginError && <div className="text-xs text-red-600">{loginError}</div>}
          </div>
        ) : (
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-500">Signed in as</div>
              <div className="font-medium text-gray-800">{role.toUpperCase()}</div>
            </div>
            <button onClick={onLogout} className="text-sm text-red-600">Logout</button>
          </div>
        )}
      </div>

      <div className="space-y-6 flex-1 overflow-y-auto pr-2">
        <div>
          <h2 className="text-sm font-semibold text-gray-700 mb-3">
            Interaction Mode
          </h2>
          <div className="space-y-2">
            <button
              onClick={() => onModeChange('add-node')}
              className={`w-full flex items-center gap-3 p-3 rounded-lg border-2 transition-all ${
                mode === 'add-node'
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 text-gray-700 hover:border-gray-300'
              }`}
            >
              <MousePointer size={20} />
              <span className="font-medium">Add Node</span>
            </button>

            <button
              onClick={() => onModeChange('connect-nodes')}
              className={`w-full flex items-center gap-3 p-3 rounded-lg border-2 transition-all ${
                mode === 'connect-nodes'
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 text-gray-700 hover:border-gray-300'
              }`}
            >
              <Link size={20} />
              <span className="font-medium">Connect Nodes</span>
            </button>

            <button
              onClick={() => onModeChange('view-route')}
              className={`w-full flex items-center gap-3 p-3 rounded-lg border-2 transition-all ${
                mode === 'view-route'
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 text-gray-700 hover:border-gray-300'
              }`}
            >
              <Eye size={20} />
              <span className="font-medium">View Route</span>
            </button>
          </div>
        </div>

        {/* Role-specific sections */}
        {role === 'admin' && (
          <div>
            <h2 className="text-sm font-semibold text-gray-700 mb-3">Admin</h2>
            <div className="space-y-2">
              <button
                onClick={() => onModeChange('add-node')}
                className="w-full p-2 rounded border text-sm"
              >
                Build Playground
              </button>
              <div className="mt-2">
                <label className="text-xs text-gray-500">Scale</label>
                <select
                  value={scale.label}
                  onChange={(e) => {
                    const selected = scales.find((s) => s.label === e.target.value);
                    if (selected) onScaleChange(selected);
                  }}
                  className="w-full p-2 border rounded mt-1"
                >
                  {scales.map((s) => (
                    <option key={s.label} value={s.label}>
                      {s.label}
                    </option>
                  ))}
                </select>
              </div>
              <button 
                onClick={onViewReports}
                className="w-full p-2 rounded border text-sm mt-2 hover:bg-blue-50 hover:border-blue-300 transition"
              >
                View Reports
              </button>
              <button 
                onClick={() => {
                  if (confirm('⚠️ Clear ALL hospitals, edges, and data from database? This cannot be undone.')) {
                    fetch('http://localhost:8000/api/reports/reset', { method: 'POST' })
                      .then(() => {
                        alert('✅ Database cleared! Refresh to see empty playground.');
                        window.location.reload();
                      })
                      .catch(err => alert('Error clearing data: ' + err.message));
                  }
                }}
                className="w-full p-2 rounded border text-sm mt-1 hover:bg-red-50 hover:border-red-300 transition text-red-600 font-semibold"
              >
                Clear All Data
              </button>
            </div>
          </div>
        )}

        {role === 'staff' && (
          <div>
            <h2 className="text-sm font-semibold text-gray-700 mb-3">Staff</h2>
            <div className="space-y-2">
              <label className="text-xs text-gray-500">Select hospital to update waste</label>
                <select
                  value={selectedNodeId ?? ''}
                  onChange={(e) => setSelectedNodeId(e.target.value)}
                  className="w-full p-2 border rounded"
                >
                  <option value="">-- Select hospital --</option>
                  {nodes
                    .filter((n) => n.type === 'hospital')
                    .map((n) => (
                      <option key={n.id} value={n.id}>
                        {n.id} - {n.waste ?? '0'}u
                      </option>
                    ))}
                </select>
              <div className="flex gap-2">
                <input
                  type="number"
                  placeholder="New waste amount"
                  className="flex-1 p-2 border rounded"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && selectedNodeId) {
                      const val = Number((e.target as HTMLInputElement).value);
                      if (!Number.isNaN(val)) onUpdateWaste(selectedNodeId, val);
                    }
                  }}
                />
                <button
                  onClick={() => {
                    const sel = (document.querySelector('select') as HTMLSelectElement)?.value;
                    const input = (document.querySelector('input[type=number]') as HTMLInputElement)?.value;
                    const val = Number(input);
                    if (sel && !Number.isNaN(val)) onUpdateWaste(sel, val);
                  }}
                  className="p-2 bg-blue-600 text-white rounded"
                >
                  Update
                </button>
              </div>
            </div>
          </div>
        )}

        {role === 'driver' && (
          <div>
            <h2 className="text-sm font-semibold text-gray-700 mb-3">Collection driver</h2>
            <div className="space-y-2">
              <button onClick={onVisualizeRoute} className="w-full p-2 bg-green-600 text-white rounded">
                View optimized route
              </button>

              <div>
                <label className="text-xs text-gray-500">Select node (hospital/disposal)</label>
                <select
                  value={selectedDriverNode ?? ''}
                  onChange={(e) => setSelectedDriverNode(e.target.value)}
                  className="w-full p-2 border rounded mt-1"
                >
                  <option value="">-- Select node --</option>
                  {nodes.map((n) => (
                    <option key={n.id} value={n.id}>
                      {n.id} - {n.type}
                    </option>
                  ))}
                </select>
              </div>

              <button
                onClick={() => {
                  if (!selectedDriverNode) return;
                  if (!confirm('Mark pickup done at ' + selectedDriverNode + '? This will remove adjacent edges.')) return;
                  onDriverMarkPickupDone(selectedDriverNode);
                  setSelectedDriverNode(null);
                }}
                disabled={!selectedDriverNode}
                className={`w-full p-2 mt-2 rounded ${selectedDriverNode ? 'border bg-white' : 'bg-gray-100 text-gray-300 cursor-not-allowed'}`}
              >
                Mark pickup done (remove adjacent edges)
              </button>
            </div>
          </div>
        )}

        <div>
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Scale</h2>
          <select
            value={scale.label}
            onChange={(e) => {
              const selected = scales.find((s) => s.label === e.target.value);
              if (selected) onScaleChange(selected);
            }}
            className="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
          >
            {scales.map((s) => (
              <option key={s.label} value={s.label}>
                {s.label}
              </option>
            ))}
          </select>
          <p className="text-xs text-gray-500 mt-2">
            1 canvas unit = {scale.factor} {scale.unit}
          </p>
        </div>

        <div className="pt-6 border-t border-gray-200">
          <button
            onClick={onVisualizeRoute}
            disabled={!canVisualizeRoute}
            className={`w-full flex items-center justify-center gap-2 p-4 rounded-lg font-medium transition-all ${
              canVisualizeRoute
                ? 'bg-green-600 text-white hover:bg-green-700'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            <Play size={20} />
            Visualize Route
          </button>
          <p className="text-xs text-gray-500 mt-2 text-center">
            {canVisualizeRoute
              ? 'Click to animate mock route'
              : 'Add nodes and edges first'}
          </p>
        </div>
      </div>

      <div className="pt-6 border-t border-gray-200 mt-auto">
        <div className="flex gap-2 mb-3">
          <button
            onClick={onUndo}
            disabled={!canUndo}
            className={`flex-1 p-2 rounded-lg border-2 transition-all ${
              canUndo
                ? 'bg-white text-gray-700 hover:bg-gray-50'
                : 'bg-gray-100 text-gray-300 cursor-not-allowed'
            }`}
          >
            Undo
          </button>

          <button
            onClick={onRedo}
            disabled={!canRedo}
            className={`flex-1 p-2 rounded-lg border-2 transition-all ${
              canRedo
                ? 'bg-white text-gray-700 hover:bg-gray-50'
                : 'bg-gray-100 text-gray-300 cursor-not-allowed'
            }`}
          >
            Redo
          </button>
        </div>
        <button
          onClick={onClear}
          className="w-full flex items-center justify-center gap-2 p-3 rounded-lg border-2 border-red-200 text-red-600 hover:bg-red-50 transition-all"
        >
          <Trash2 size={18} />
          Clear All
        </button>
      </div>
    </div>
  );
}
