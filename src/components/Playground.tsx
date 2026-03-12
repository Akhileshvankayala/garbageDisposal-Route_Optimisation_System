import { useState, useRef, useEffect } from 'react';
import { Node, Edge, Mode, Scale, Role } from '../types';
import { calculatePixelDistance, convertToRealDistance } from '../utils/geometry';

interface PlaygroundProps {
  nodes: Node[];
  edges: Edge[];
  mode: Mode;
  scale: Scale;
  onNodeCreate: (node: Node) => void;
  onEdgeCreate: (edge: Edge) => void;
  animatingRoute: string[];
  animationStep: number;
  role: Role;
}

export default function Playground({
  nodes,
  edges,
  mode,
  scale,
  onNodeCreate,
  onEdgeCreate,
  animatingRoute,
  animationStep,
  role,
}: PlaygroundProps) {
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const canvasRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (mode !== 'connect-nodes') {
      setSelectedNode(null);
    }
  }, [mode]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!canvasRef.current) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (mode === 'add-node') {
      onNodeCreate({ id: '', type: 'hospital', x, y });
    }
  };

  const handleNodeClick = (nodeId: string, e: React.MouseEvent) => {
    e.stopPropagation();

    if (mode === 'connect-nodes') {
      if (!selectedNode) {
        setSelectedNode(nodeId);
      } else if (selectedNode !== nodeId) {
        const fromNode = nodes.find((n) => n.id === selectedNode);
        const toNode = nodes.find((n) => n.id === nodeId);

        if (fromNode && toNode) {
          const edgeExists = edges.some(
            (e) =>
              (e.from === selectedNode && e.to === nodeId) ||
              (e.from === nodeId && e.to === selectedNode)
          );

          if (!edgeExists) {
            const pixelDist = calculatePixelDistance(
              fromNode.x,
              fromNode.y,
              toNode.x,
              toNode.y
            );
            const realDist = convertToRealDistance(pixelDist, scale.factor);

            onEdgeCreate({
              from: selectedNode,
              to: nodeId,
              distance: realDist,
            });
          }
        }

        setSelectedNode(null);
      } else {
        setSelectedNode(null);
      }
    }
  };

  const isEdgeAnimating = (from: string, to: string): boolean => {
    if (animationStep < 0 || animationStep >= animatingRoute.length - 1) {
      return false;
    }

    const currentFrom = animatingRoute[animationStep];
    const currentTo = animatingRoute[animationStep + 1];

    return (
      (from === currentFrom && to === currentTo) ||
      (from === currentTo && to === currentFrom)
    );
  };

  const isEdgeInCompletedRoute = (from: string, to: string): boolean => {
    for (let i = 0; i < animationStep; i++) {
      if (i < animatingRoute.length - 1) {
        const routeFrom = animatingRoute[i];
        const routeTo = animatingRoute[i + 1];

        if (
          (from === routeFrom && to === routeTo) ||
          (from === routeTo && to === routeFrom)
        ) {
          return true;
        }
      }
    }
    return false;
  };

  const getNodeColor = (type: string) => {
    return type === 'hospital' ? 'text-blue-600' : 'text-green-600';
  };

  const getNodeBgColor = (type: string) => {
    return type === 'hospital' ? 'bg-blue-100' : 'bg-green-100';
  };

  const getNodeBorderColor = (nodeId: string) => {
    if (selectedNode === nodeId) return 'border-blue-600';
    if (hoveredNode === nodeId) return 'border-gray-400';
    return 'border-gray-300';
  };

  return (
    <div
      ref={canvasRef}
      onClick={handleCanvasClick}
      className="relative w-full h-full bg-gray-50 overflow-hidden cursor-crosshair"
      style={{
        backgroundImage: `
          linear-gradient(to right, #e5e7eb 1px, transparent 1px),
          linear-gradient(to bottom, #e5e7eb 1px, transparent 1px)
        `,
        backgroundSize: '40px 40px',
      }}
    >
      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        {edges.map((edge, idx) => {
          const fromNode = nodes.find((n) => n.id === edge.from);
          const toNode = nodes.find((n) => n.id === edge.to);

          if (!fromNode || !toNode) return null;

          const isAnimating = isEdgeAnimating(edge.from, edge.to);
          const isCompleted = isEdgeInCompletedRoute(edge.from, edge.to);
          const isAdminViewRoute = mode === 'view-route' && role === 'admin';

          const midX = (fromNode.x + toNode.x) / 2;
          const midY = (fromNode.y + toNode.y) / 2;

          return (
            <g key={idx}>
              <line
                x1={fromNode.x}
                y1={fromNode.y}
                x2={toNode.x}
                y2={toNode.y}
                stroke={isAdminViewRoute ? '#10b981' : isAnimating || isCompleted ? '#10b981' : '#9ca3af'}
                strokeWidth={isAdminViewRoute ? 3 : isAnimating ? 4 : isCompleted ? 3 : 2}
                className="transition-all duration-300"
              />
              <circle cx={midX} cy={midY} r="20" fill="white" stroke="#d1d5db" strokeWidth="2" />
              <text
                  x={midX}
                  y={midY}
                  textAnchor="middle"
                  dy=".3em"
                  className={`text-xs font-medium pointer-events-none ${isAdminViewRoute ? 'fill-green-700' : 'fill-gray-700'}`}
                >
                  {Number(edge.distance).toFixed(1)}
                </text>
            </g>
          );
        })}
      </svg>

      {nodes.map((node) => {
        const emoji = node.type === 'hospital' ? '🏥' : '🗑️';
        const isAdminViewRoute = mode === 'view-route' && role === 'admin';
        return (
          <div
            key={node.id}
            onClick={(e) => handleNodeClick(node.id, e)}
            onMouseEnter={() => setHoveredNode(node.id)}
            onMouseLeave={() => setHoveredNode(null)}
            className={`absolute flex flex-col items-center gap-2 cursor-pointer transition-all ${
              mode === 'connect-nodes' ? 'hover:scale-110' : ''
            } ${isAdminViewRoute ? 'opacity-50 filter grayscale' : ''}`}
            style={{
              left: node.x,
              top: node.y,
              transform: 'translate(-50%, -50%)',
            }}
          >
            <div
              className={`p-3 rounded-full border-4 ${getNodeBgColor(
                node.type
              )} ${getNodeBorderColor(node.id)} shadow-lg transition-all ${isAdminViewRoute ? 'bg-gray-100' : ''}`}
            >
              <span className="text-2xl">{emoji}</span>
            </div>
            <div className="flex flex-col items-center gap-1">
              <div className="bg-white px-2 py-1 rounded shadow border border-gray-200">
                <span className="text-xs font-bold text-gray-700">{node.id}</span>
              </div>
              {node.waste !== undefined && (
                <div className="bg-blue-500 text-white px-2 py-0.5 rounded text-xs font-medium">
                  {node.waste}u
                </div>
              )}
            </div>
          </div>
        );
      })}

      {/* Truck marker for simple animation: shows truck at the current animation node */}
      {animationStep >= 0 && animatingRoute.length > 0 && animatingRoute[animationStep] && (() => {
        const currentId = animatingRoute[animationStep];
        const currentNode = nodes.find((n) => n.id === currentId);
        if (!currentNode) return null;

        return (
          <div
            style={{
              left: currentNode.x,
              top: currentNode.y - 36,
              transform: 'translate(-50%, -50%)',
            }}
            className="absolute pointer-events-none"
          >
            <div className="text-2xl animate-bounce">🚚</div>
          </div>
        );
      })()}

      {mode === 'add-node' && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg text-sm font-medium">
          Click anywhere to add a node
        </div>
      )}

      {mode === 'connect-nodes' && !selectedNode && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg text-sm font-medium">
          Click first node to start connection
        </div>
      )}

      {mode === 'connect-nodes' && selectedNode && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg text-sm font-medium">
          Click second node to complete connection
        </div>
      )}
    </div>
  );
}
