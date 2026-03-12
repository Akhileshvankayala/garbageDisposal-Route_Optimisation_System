import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Playground from './components/Playground';
import NodeModal from './components/NodeModal';
import ReportsPanel from './components/ReportsPanel';
import { postNode, postEdge, computeRoute } from './utils/api';
import ScaleIndicator from './components/ScaleIndicator';
import MetricsPanel from './components/MetricsPanel';
import { Node, Edge, Mode, Scale, NodeType, Role } from './types';

const SCALES: Scale[] = [
  { label: '1 unit = 10 meters', factor: 0.1, unit: 'm' },
  { label: '1 unit = 50 meters', factor: 0.5, unit: 'm' },
  { label: '1 unit = 100 meters', factor: 1, unit: 'm' },
  { label: '1 unit = 1 km', factor: 10, unit: 'm' },
];

function App() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [undoStack, setUndoStack] = useState<Array<{nodes: Node[]; edges: Edge[]}>>([]);
  const [redoStack, setRedoStack] = useState<Array<{nodes: Node[]; edges: Edge[]}>>([]);
  const [mode, setMode] = useState<Mode>('add-node');
  const [scale, setScale] = useState<Scale>(SCALES[2]);
  const [showModal, setShowModal] = useState(false);
  const [pendingNodePosition, setPendingNodePosition] = useState<{
    x: number;
    y: number;
  } | null>(null);
  const [idCounters, setIdCounters] = useState<{ hospital: number; disposal: number }>({
    hospital: 1,
    disposal: 1,
  });
  const [animatingRoute, setAnimatingRoute] = useState<string[]>([]);
  const [animationStep, setAnimationStep] = useState(-1);
  const [showMetrics, setShowMetrics] = useState(false);
  const [role, setRole] = useState<Role>('guest');
  const [loginError, setLoginError] = useState<string | null>(null);
  const [showReports, setShowReports] = useState(false);
  const [lastRouteData, setLastRouteData] = useState<any>(null);
  const [routeCompleted, setRouteCompleted] = useState(false);

  const hospitalCount = nodes.filter((n) => n.type === 'hospital').length;
  const disposalCount = nodes.filter((n) => n.type === 'disposal').length;

  useEffect(() => {
    if (animationStep >= 0 && animationStep < animatingRoute.length - 1) {
      const timer = setTimeout(() => {
        setAnimationStep(animationStep + 1);
      }, 600);

      return () => clearTimeout(timer);
    } else if (animationStep >= animatingRoute.length - 1 && animatingRoute.length > 0) {
      setShowMetrics(true);
      // Animation completed - update waste levels in frontend
      if (lastRouteData && !routeCompleted) {
        console.log('✅ Animation complete! Updating waste in Playground...');
        updateFrontendWaste(lastRouteData);
        setRouteCompleted(true);
      }
    }
  }, [animationStep, animatingRoute, lastRouteData, routeCompleted]);

  // Keyboard shortcuts: Ctrl+Z undo, Ctrl+Shift+Z redo
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') {
        e.preventDefault();
        if (e.shiftKey) {
          handleRedo();
        } else {
          handleUndo();
        }
      }
    };

    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [undoStack, redoStack, nodes, edges]);

  const handleNodeCreate = (node: Node) => {
    setShowModal(true);
    setPendingNodePosition({ x: node.x, y: node.y });
  };

  const handleNodeTypeSelect = (type: NodeType) => {
    if (!pendingNodePosition) return;

    const prefix = type === 'hospital' ? 'H' : 'D';
    const count = type === 'hospital' ? idCounters.hospital : idCounters.disposal;
    const id = `${prefix}${count}`;

    const newNode: Node = {
      id,
      type,
      x: pendingNodePosition.x,
      y: pendingNodePosition.y,
      waste: type === 'hospital' ? Math.floor(Math.random() * 30) + 20 : undefined,
      hospital_id: undefined, // Will be set from API response
    };

    // push previous state to undo stack
    setUndoStack((s) => [...s, { nodes: nodes.slice(), edges: edges.slice() }]);
    setRedoStack([]);

    setNodes((prev) => [...prev, newNode]);

    // stop any running animation when graph changes
    setAnimatingRoute([]);
    setAnimationStep(-1);

    // advance id counter to avoid duplicates
    setIdCounters((c) => ({
      ...c,
      hospital: type === 'hospital' ? c.hospital + 1 : c.hospital,
      disposal: type === 'disposal' ? c.disposal + 1 : c.disposal,
    }));

    // Persist node to backend and capture the hospital_id
    postNode({ label: newNode.id, pixel_x: newNode.x, pixel_y: newNode.y, type: newNode.type })
      .then((response: any) => {
        if (response && response.hospital_id) {
          // Update the node with the actual hospital_id from the backend
          setNodes((prev) =>
            prev.map((n) =>
              n.id === newNode.id ? { ...n, hospital_id: response.hospital_id } : n
            )
          );
          console.log(`Node ${newNode.id} created with hospital_id: ${response.hospital_id}`);
        }
      })
      .catch(() => {
        // OK: placeholder failure should not block UX
      });
    setShowModal(false);
    setPendingNodePosition(null);
  };

  const handleEdgeCreate = (edge: Edge) => {
    // push previous state to undo stack
    setUndoStack((s) => [...s, { nodes: nodes.slice(), edges: edges.slice() }]);
    setRedoStack([]);

    // Prevent creating duplicate edges in UI and backend
    const exists = edges.some(
      (e) => (e.from === edge.from && e.to === edge.to) || (e.from === edge.to && e.to === edge.from)
    );
    if (exists) {
      console.warn('Edge already exists in UI, skipping creation:', edge.from, '->', edge.to);
      return;
    }

    setEdges((prev) => [...prev, edge]);

    // stop any running animation when graph changes
    setAnimatingRoute([]);
    setAnimationStep(-1);

    // try to persist edge (placeholder)
    postEdge({ from: edge.from, to: edge.to, pixel_length: edge.distance }).catch(() => {});
  };

  const handleClear = () => {
    if (nodes.length > 0 || edges.length > 0) {
      if (window.confirm('Are you sure you want to clear all nodes and edges?')) {
        setUndoStack((s) => [...s, { nodes: nodes.slice(), edges: edges.slice() }]);
        setRedoStack([]);

        setNodes([]);
        setEdges([]);
        setAnimatingRoute([]);
        setAnimationStep(-1);
        setShowMetrics(false);
      }
    }
  };

  const handleLogin = (selectedRole: Role, password: string) => {
    // Simple client-side password check (per requirement)
    const ok =
      (selectedRole === 'admin' && password === 'Admin') ||
      (selectedRole === 'staff' && password === 'Staff') ||
      (selectedRole === 'driver' && password === 'driver');

    if (ok) {
      setRole(selectedRole);
      setLoginError(null);
      // Non-admin/staff cannot set mode to add-node/connect unless admin
      if (selectedRole === 'staff') setMode('view-route');
    } else {
      setLoginError('Invalid password for selected role');
    }
  };

  const handleLogout = () => {
    setRole('guest');
    setLoginError(null);
  };

  const handleUpdateWaste = (nodeId: string, amount: number) => {
    setNodes((prev) => prev.map((n) => (n.id === nodeId ? { ...n, waste: amount } : n)));
    // optionally send to backend later
    postNode({ id: nodeId, waste: amount }).catch(() => {});
  };

  const handleDriverMarkPickupDone = (nodeId: string) => {
    // Remove adjacent edges to the selected node and optionally zero out waste
    const prev = { nodes: nodes.slice(), edges: edges.slice() };
    setUndoStack((s) => [...s, prev]);
    setRedoStack([]);

    const remainingEdges = edges.filter((e) => e.from !== nodeId && e.to !== nodeId);
    setEdges(remainingEdges);

    // zero out waste for hospital nodes
    setNodes((prevNodes) => prevNodes.map((n) => (n.id === nodeId ? { ...n, waste: 0 } : n)));

    // Stop any running animation
    setAnimatingRoute([]);
    setAnimationStep(-1);

    // Persist change (placeholder)
    postEdge({ remove_adjacent_to: nodeId }).catch(() => {});
    postNode({ id: nodeId, waste: 0 }).catch(() => {});
  };

  const handleModeChange = (m: Mode) => {
    // Only admin may switch to add/connect modes
    if (m === 'view-route') {
      setMode(m);
      return;
    }
    if (role !== 'admin') {
      alert('Only Admin can change interaction mode');
      return;
    }
    setMode(m);
  };

  const handleUndo = () => {
    const last = undoStack[undoStack.length - 1];
    if (!last) return;

    setRedoStack((s) => [...s, { nodes: nodes.slice(), edges: edges.slice() }]);
    setNodes(last.nodes);
    setEdges(last.edges);
    setUndoStack((s) => s.slice(0, -1));
    setAnimatingRoute([]);
    setAnimationStep(-1);
    setShowMetrics(false);
  };

  const handleRedo = () => {
    const last = redoStack[redoStack.length - 1];
    if (!last) return;

    setUndoStack((s) => [...s, { nodes: nodes.slice(), edges: edges.slice() }]);
    setNodes(last.nodes);
    setEdges(last.edges);
    setRedoStack((s) => s.slice(0, -1));
    setAnimatingRoute([]);
    setAnimationStep(-1);
    setShowMetrics(false);
  };

  const handleVisualizeRoute = () => {
    const hospitals = nodes.filter((n) => n.type === 'hospital');
    const disposals = nodes.filter((n) => n.type === 'disposal');

    if (hospitals.length === 0 || disposals.length === 0) {
      alert('❌ Need at least 1 hospital and 1 disposal center!');
      return;
    }

    console.log('🔄 [STEP 1] Starting route visualization...');
    const depot = disposals[0].id;
    setRouteCompleted(false);

    computeRoute({ 
      truck_id: 1, 
      targets: hospitals.map((h) => parseInt(h.id.replace('H', ''), 10)), 
      disposal_threshold: 0.8 
    })
      .then((res) => {
        if (res && res.path && Array.isArray(res.path) && res.path.length > 0) {
          console.log('✅ [STEP 2] Route computed:', {
            distance: res.total_distance_m,
            waste_collected: res.total_waste_collected_kg,
            disposal_trips: res.disposal_trips,
            events: res.events
          });
          
          // Store route data for later use
          setLastRouteData(res);
          setAnimatingRoute(res.path.map(String));
          
          console.log('⏳ [STEP 3] Saving route to database...');
          // Save route to database with better error handling
          return saveRouteToDatabase({
            vehicle_id: 1,
            driver_id: 3,
            path: res.path,
            total_distance_m: res.total_distance_m || 0,
            total_waste_collected_kg: res.total_waste_collected_kg || 0,
            disposal_trips: res.disposal_trips || 0,
            events: res.events || [],
          }).then((saveResult) => {
            if (saveResult && saveResult.success) {
              console.log('✅ Route saved to database');
              
              console.log('⏳ [STEP 4] Updating waste in database...');
              // Update waste in database
              return updateWasteLevels(res).then((wasteResult) => {
                if (wasteResult && wasteResult.success) {
                  console.log('✅ Waste decreased in database');
                } else {
                  console.warn('⚠️ Waste update completed with issues');
                }
              });
            } else {
              console.warn('⚠️ Route save completed with issues');
            }
          }).catch((err) => {
            console.error('❌ Error in save/update chain:', err);
          });
        } else {
          console.warn('⚠️ Route computation failed, using mock route');
          const mockRoute: string[] = [depot, ...hospitals.map((h) => h.id), depot];
          setAnimatingRoute(mockRoute);
        }
      })
      .catch((err) => {
        console.error('❌ Error computing route:', err);
        const mockRoute: string[] = [depot, ...hospitals.map((h) => h.id), depot];
        setAnimatingRoute(mockRoute);
      })
      .finally(() => {
        setAnimationStep(0);
        setShowMetrics(false);
      });
  };

  const updateFrontendWaste = (routeData: any) => {
    "Update frontend nodes to show decreased waste after animation completes";
    const wasteReductions: { [key: string]: number } = {};
    
    // Extract waste from pickup events
    if (routeData.events && Array.isArray(routeData.events)) {
      routeData.events.forEach((event: any) => {
        if (event.event_type === 'pickup' && event.node_id && event.node_id !== 1) {
          wasteReductions[String(event.node_id)] = event.amount_kg || 0;
        }
      });
    }
    
    console.log('📊 Updating frontend nodes with waste reductions:', wasteReductions);
    
    // Update nodes to reflect decreased waste
    setNodes(prev => {
      return prev.map(node => {
        const hospitalId = parseInt(node.id.replace(/[HD]/g, ''), 10);
        const wasCollected = wasteReductions[String(hospitalId)] || 0;
        
        if (wasCollected > 0 && node.type === 'hospital') {
          const oldWaste = node.waste || 0;
          const newWaste = Math.max(0, oldWaste - wasCollected);
          console.log(`  📉 ${node.id}: ${oldWaste}kg → ${newWaste}kg (collected: ${wasCollected}kg)`);
          return { ...node, waste: newWaste };
        }
        return node;
      });
    });
  };

  const saveRouteToDatabase = async (routeData: any) => {
    try {
      // Validate routeData
      if (!routeData || typeof routeData !== 'object') {
        console.warn('⚠️ Invalid route data:', routeData);
        return { success: false };
      }

      console.log('💾 Saving route with data:', routeData);
      const response = await fetch('http://localhost:8000/api/route/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(routeData),
      });

      if (!response) {
        console.error('❌ No response from server');
        return { success: false };
      }

      if (response.ok) {
        const saved = await response.json();
        console.log('✅ Route saved successfully:', saved);
        return { success: true, saved };
      } else {
        const error = await response.text();
        console.error('❌ Failed to save route:', response.status, error);
        return { success: false };
      }
    } catch (err) {
      console.error('❌ Error saving route:', err);
      return { success: false };
    }
  };

  const updateWasteLevels = async (routeResult: any) => {
    try {
      // Validate routeResult
      if (!routeResult || typeof routeResult !== 'object') {
        console.warn('Invalid route result:', routeResult);
        return { success: true };
      }

      const hospitalUpdates: { [key: string]: number } = {};
      
      // Extract waste amounts from route events
      if (routeResult.events && Array.isArray(routeResult.events)) {
        routeResult.events.forEach((event: any) => {
          // Only process pickup events (not disposal events)
          if (event && event.event_type === 'pickup' && event.node_id && event.node_id !== 1) {
            const hospitalId = String(event.node_id);
            hospitalUpdates[hospitalId] = event.amount_kg || 0;
          }
        });
      }
      
      if (Object.keys(hospitalUpdates).length > 0) {
        console.log('Sending waste updates to backend:', hospitalUpdates);
        const response = await fetch('http://localhost:8000/api/route/update-waste', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ hospitals: hospitalUpdates }),
        });
        
        if (!response) {
          console.error('No response from server');
          return { success: false };
        }

        if (response.ok) {
          const updated = await response.json();
          console.log('Waste updated in database:', updated);
          
          // IMMEDIATELY update frontend nodes with fresh data from backend
          console.log('Refreshing hospital data from backend...');
          const updatedNodesData = await fetch('http://localhost:8000/api/nodes').then(r => r.json());
          
          // Update nodes with new waste levels using hospital_id for matching
          setNodes((prevNodes) =>
            prevNodes.map((n) => {
              // Use node.hospital_id directly if available
              if (n.hospital_id !== undefined) {
                const hospitalData = updatedNodesData.find(
                  (h: any) => h.hospital_id === n.hospital_id
                );
                if (hospitalData) {
                  console.log(`Updated ${n.id}: waste = ${hospitalData.current_waste_kg}kg (matched via hospital_id ${n.hospital_id})`);
                  return {
                    ...n,
                    waste: hospitalData.current_waste_kg,
                  };
                }
              }
              return n;
            })
          );
          
          return { success: true, updated };
        } else {
          console.error('Failed to update waste:', response.statusText);
          return { success: false };
        }
      } else {
        console.log('No pickup events to process');
        return { success: true };
      }
    } catch (err) {
      console.error('Error updating waste:', err);
      return { success: false };
    }
  };

  const refreshHospitalWasteLevels = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/nodes', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response || !response.ok) {
        console.warn('⚠️ Could not refresh hospital data');
        return;
      }

      const hospitalsData = await response.json();
      console.log('📊 Fetched updated hospital data:', hospitalsData);

      // Update nodes with new waste levels
      if (Array.isArray(hospitalsData)) {
        setNodes((prevNodes) =>
          prevNodes.map((node) => {
            // Use node.hospital_id directly if available
            const updated = node.hospital_id !== undefined
              ? hospitalsData.find((h: any) => h.hospital_id === node.hospital_id)
              : null;
            
            if (updated) {
              return {
                ...node,
                waste: updated.current_waste_kg || 0,
              };
            }
            return node;
          })
        );
        console.log('✅ Hospital waste levels refreshed');
      }
    } catch (err) {
      console.error('⚠️ Error refreshing hospital data:', err);
    }
  };

  const canVisualizeRoute =
    nodes.some((n) => n.type === 'hospital') &&
    nodes.some((n) => n.type === 'disposal') &&
    edges.length > 0;

  const calculateRouteMetrics = () => {
    // Use actual route data if available, otherwise show 0s
    if (lastRouteData && lastRouteData.path) {
      return {
        totalDistance: lastRouteData.total_distance_m || 0,
        wasteCollected: lastRouteData.total_waste_collected_kg || 0,
        disposalTrips: lastRouteData.disposal_trips || 0,
      };
    }
    
    // Show 0s when no route has been computed
    return {
      totalDistance: 0,
      wasteCollected: 0,
      disposalTrips: 0,
    };
  };

  const metrics = calculateRouteMetrics();

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <Sidebar
        mode={mode}
        onModeChange={handleModeChange}
        scale={scale}
        onScaleChange={setScale}
        scales={SCALES}
        onClear={handleClear}
        onVisualizeRoute={handleVisualizeRoute}
        canVisualizeRoute={canVisualizeRoute}
        onUndo={handleUndo}
        onRedo={handleRedo}
        canUndo={undoStack.length > 0}
        canRedo={redoStack.length > 0}
        role={role}
        onLogin={handleLogin}
        onLogout={handleLogout}
        loginError={loginError}
        nodes={nodes}
        onUpdateWaste={handleUpdateWaste}
        onDriverMarkPickupDone={handleDriverMarkPickupDone}
        onViewReports={() => setShowReports(true)}
      />

      <div className="flex-1 relative">
        <Playground
          nodes={nodes}
          edges={edges}
          mode={mode}
          scale={scale}
          role={role}
          onNodeCreate={handleNodeCreate}
          onEdgeCreate={handleEdgeCreate}
          animatingRoute={animatingRoute}
          animationStep={animationStep}
        />

        <ScaleIndicator scale={scale} />

        <MetricsPanel
          totalDistance={metrics.totalDistance}
          wasteCollected={metrics.wasteCollected}
          disposalTrips={metrics.disposalTrips}
          unit={scale.unit}
          isVisible={showMetrics}
        />

        <div className="absolute top-6 left-6 bg-white border-2 border-gray-300 rounded-lg px-4 py-3 shadow-md">
          <div className="flex gap-6 text-sm">
            <div>
              <span className="text-gray-500">Hospitals:</span>{' '}
              <span className="font-bold text-blue-600">{hospitalCount}</span>
            </div>
            <div>
              <span className="text-gray-500">Disposal Centers:</span>{' '}
              <span className="font-bold text-green-600">{disposalCount}</span>
            </div>
            <div>
              <span className="text-gray-500">Connections:</span>{' '}
              <span className="font-bold text-gray-700">{edges.length}</span>
            </div>
          </div>
        </div>
      </div>

      {showModal && (
        <NodeModal
          onSelect={handleNodeTypeSelect}
          onClose={() => {
            setShowModal(false);
            setPendingNodePosition(null);
          }}
        />
      )}

      <ReportsPanel
        isOpen={showReports}
        onClose={() => setShowReports(false)}
      />
    </div>
  );
}

export default App;
