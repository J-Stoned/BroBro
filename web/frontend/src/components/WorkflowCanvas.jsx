import React, { useState, useRef, useEffect, useCallback } from 'react';
import WorkflowNode from './WorkflowNode';
import WorkflowConnection from './WorkflowConnection';

/**
 * WorkflowCanvas Component
 * Epic 10: Story 10.1
 *
 * Main SVG canvas for rendering workflow with zoom, pan, drag functionality
 */

const WorkflowCanvas = ({
  workflow,
  selectedNodeId,
  onNodeSelect,
  onNodeMove,
  onConnectionSelect,
  readonly = false
}) => {
  const svgRef = useRef(null);
  const [viewportZoom, setViewportZoom] = useState(1);
  const [viewportPan, setViewportPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const [draggedNode, setDraggedNode] = useState(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [hoveredConnection, setHoveredConnection] = useState(null);
  const [selectedConnectionId, setSelectedConnectionId] = useState(null);
  const [spacePressed, setSpacePressed] = useState(false);

  // Handle keyboard events
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === ' ' && !e.repeat) {
        setSpacePressed(true);
      }
      if (e.key === 'Delete' && selectedNodeId && !readonly) {
        // Delete node (handled by parent)
      }
    };

    const handleKeyUp = (e) => {
      if (e.key === ' ') {
        setSpacePressed(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [selectedNodeId, readonly]);

  // Handle mouse wheel zoom
  const handleWheel = useCallback((e) => {
    if (readonly) return;

    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    const newZoom = Math.max(0.5, Math.min(3, viewportZoom * delta));

    setViewportZoom(newZoom);
  }, [viewportZoom, readonly]);

  // Handle canvas click (deselect)
  const handleCanvasClick = (e) => {
    if (e.target === svgRef.current || e.target.classList.contains('grid-background')) {
      onNodeSelect(null);
      setSelectedConnectionId(null);
    }
  };

  // Handle mouse down on canvas (start panning)
  const handleMouseDown = (e) => {
    if (readonly) return;

    if (spacePressed || e.button === 1) { // Space or middle mouse
      setIsPanning(true);
      setPanStart({ x: e.clientX - viewportPan.x, y: e.clientY - viewportPan.y });
      e.preventDefault();
    }
  };

  // Handle mouse move (panning or dragging)
  const handleMouseMove = useCallback((e) => {
    if (isPanning) {
      const newPanX = e.clientX - panStart.x;
      const newPanY = e.clientY - panStart.y;
      setViewportPan({ x: newPanX, y: newPanY });
    }

    if (draggedNode && !readonly) {
      const svg = svgRef.current;
      if (!svg) return;

      const rect = svg.getBoundingClientRect();
      const x = (e.clientX - rect.left - viewportPan.x - dragOffset.x) / viewportZoom;
      const y = (e.clientY - rect.top - viewportPan.y - dragOffset.y) / viewportZoom;

      // Snap to grid (20px)
      const snappedX = Math.round(x / 20) * 20;
      const snappedY = Math.round(y / 20) * 20;

      if (onNodeMove) {
        onNodeMove(draggedNode, { x: snappedX, y: snappedY });
      }
    }
  }, [isPanning, draggedNode, panStart, viewportPan, viewportZoom, dragOffset, onNodeMove, readonly]);

  // Handle mouse up (stop panning/dragging)
  const handleMouseUp = useCallback(() => {
    setIsPanning(false);
    setDraggedNode(null);
  }, []);

  // Add mouse move/up listeners
  useEffect(() => {
    if (isPanning || draggedNode) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);

      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isPanning, draggedNode, handleMouseMove, handleMouseUp]);

  // Handle node drag start
  const handleNodeDragStart = (e, nodeId) => {
    if (readonly) return;

    const node = workflow.nodes.find(n => n.id === nodeId);
    if (!node) return;

    const svg = svgRef.current;
    if (!svg) return;

    const rect = svg.getBoundingClientRect();
    const offsetX = (e.clientX - rect.left - viewportPan.x) / viewportZoom - node.position.x;
    const offsetY = (e.clientY - rect.top - viewportPan.y) / viewportZoom - node.position.y;

    setDragOffset({ x: offsetX, y: offsetY });
    setDraggedNode(nodeId);
  };

  // Fit to screen
  const fitToScreen = () => {
    if (!workflow.nodes || workflow.nodes.length === 0) return;

    // Calculate bounds
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;

    workflow.nodes.forEach(node => {
      minX = Math.min(minX, node.position.x);
      minY = Math.min(minY, node.position.y);
      maxX = Math.max(maxX, node.position.x + 200);
      maxY = Math.max(maxY, node.position.y + 120);
    });

    const width = maxX - minX;
    const height = maxY - minY;

    const svg = svgRef.current;
    if (!svg) return;

    const rect = svg.getBoundingClientRect();
    const scaleX = (rect.width - 100) / width;
    const scaleY = (rect.height - 100) / height;
    const newZoom = Math.min(scaleX, scaleY, 1);

    setViewportZoom(newZoom);
    setViewportPan({
      x: (rect.width - width * newZoom) / 2 - minX * newZoom,
      y: (rect.height - height * newZoom) / 2 - minY * newZoom
    });
  };

  // Grid pattern
  const gridSize = 20;
  const gridOpacity = 0.1;

  const cursor = spacePressed || isPanning ? 'grabbing' :
                 draggedNode ? 'move' :
                 'default';

  return (
    <div className="workflow-canvas-container" style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* Zoom controls */}
      <div className="canvas-controls" style={{
        position: 'absolute',
        top: '10px',
        right: '10px',
        zIndex: 10,
        display: 'flex',
        gap: '8px',
        background: 'white',
        padding: '8px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <button
          onClick={() => setViewportZoom(Math.min(3, viewportZoom * 1.2))}
          style={{
            padding: '6px 12px',
            border: '1px solid #e5e7eb',
            borderRadius: '4px',
            background: 'white',
            cursor: 'pointer',
            fontSize: '14px'
          }}
          title="Zoom In"
        >
          +
        </button>
        <button
          onClick={() => setViewportZoom(Math.max(0.5, viewportZoom * 0.8))}
          style={{
            padding: '6px 12px',
            border: '1px solid #e5e7eb',
            borderRadius: '4px',
            background: 'white',
            cursor: 'pointer',
            fontSize: '14px'
          }}
          title="Zoom Out"
        >
          −
        </button>
        <button
          onClick={fitToScreen}
          style={{
            padding: '6px 12px',
            border: '1px solid #e5e7eb',
            borderRadius: '4px',
            background: 'white',
            cursor: 'pointer',
            fontSize: '11px'
          }}
          title="Fit to Screen"
        >
          Fit
        </button>
        <div style={{
          padding: '6px 12px',
          fontSize: '11px',
          color: '#6b7280',
          display: 'flex',
          alignItems: 'center'
        }}>
          {Math.round(viewportZoom * 100)}%
        </div>
      </div>

      {/* SVG Canvas */}
      <svg
        ref={svgRef}
        width="100%"
        height="100%"
        onWheel={handleWheel}
        onClick={handleCanvasClick}
        onMouseDown={handleMouseDown}
        style={{ cursor, background: '#fafafa' }}
      >
        <defs>
          {/* Grid pattern */}
          <pattern
            id="grid"
            width={gridSize}
            height={gridSize}
            patternUnits="userSpaceOnUse"
          >
            <rect width={gridSize} height={gridSize} fill="none" />
            <path
              d={`M ${gridSize} 0 L 0 0 0 ${gridSize}`}
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="0.5"
              opacity={gridOpacity}
            />
          </pattern>
        </defs>

        {/* Grid background */}
        <rect
          width="100%"
          height="100%"
          fill="url(#grid)"
          className="grid-background"
        />

        {/* Main group with transform */}
        <g transform={`translate(${viewportPan.x}, ${viewportPan.y}) scale(${viewportZoom})`}>
          {/* Render connections first (behind nodes) */}
          {workflow.connections && workflow.connections.map(connection => {
            const fromNode = workflow.nodes.find(n => n.id === connection.from);
            const toNode = workflow.nodes.find(n => n.id === connection.to);

            return (
              <WorkflowConnection
                key={connection.id}
                connection={connection}
                fromNode={fromNode}
                toNode={toNode}
                isSelected={selectedConnectionId === connection.id}
                isHovered={hoveredConnection === connection.id}
                onSelect={setSelectedConnectionId}
                onMouseEnter={() => setHoveredConnection(connection.id)}
                onMouseLeave={() => setHoveredConnection(null)}
              />
            );
          })}

          {/* Render nodes */}
          {workflow.nodes && workflow.nodes.map(node => (
            <WorkflowNode
              key={node.id}
              node={node}
              isSelected={selectedNodeId === node.id}
              onSelect={onNodeSelect}
              onDragStart={handleNodeDragStart}
              scale={viewportZoom}
            />
          ))}
        </g>
      </svg>

      {/* Instructions overlay (bottom left) */}
      <div style={{
        position: 'absolute',
        bottom: '10px',
        left: '10px',
        background: 'rgba(255,255,255,0.95)',
        padding: '8px 12px',
        borderRadius: '6px',
        fontSize: '11px',
        color: '#6b7280',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <div><strong>Space + Drag</strong>: Pan | <strong>Scroll</strong>: Zoom | <strong>Drag Node</strong>: Move</div>
      </div>
    </div>
  );
};

export default WorkflowCanvas;
