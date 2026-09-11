import React, { useState, useRef } from 'react';
import { Detection, SonarScan } from '../../../models/types';
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  RotateCcw,
  Eye,
  EyeOff,
  Layers,
} from 'lucide-react';

interface SonarViewerProps {
  scan: SonarScan;
  detections: Detection[];
  selectedDetectionId: string | null;
  onSelectDetection: (id: string) => void;
}

export const SonarViewer: React.FC<SonarViewerProps> = ({
  scan,
  detections,
  selectedDetectionId,
  onSelectDetection,
}) => {
  const [zoom, setZoom] = useState<number>(1);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [showBoxes, setShowBoxes] = useState<boolean>(true);
  const [showLabels, setShowLabels] = useState<boolean>(true);
  const [hoveredDetectionId, setHoveredDetectionId] = useState<string | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.25, 3.5));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.25, 0.5));
  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };
  const handleFit = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 0.15 : -0.15;
    setZoom((prev) => Math.min(Math.max(prev + zoomFactor, 0.5), 3.5));
  };

  return (
    <div className="bg-[#0a0a0a] border border-white/8 rounded-2xl overflow-hidden flex flex-col h-[580px]">
      {/* Sonar Toolbar */}
      <div className="h-11 bg-[#111] border-b border-white/8 px-4 flex items-center justify-between shrink-0 select-none text-xs font-mono">
        <div className="flex items-center gap-3 text-white/60">
          <span className="flex items-center gap-1.5 font-bold text-white/70">
            <Layers className="w-3.5 h-3.5 text-white/40" />
            WATERFALL VIEW
          </span>
          <span className="text-white/20">|</span>
          <span className="text-[11px] text-white/40 truncate max-w-xs">
            {scan.instrument} • {scan.frequencyKhz} kHz
          </span>
        </div>

        {/* Toolbar Controls */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setShowBoxes(!showBoxes)}
            className={`px-2 py-1 rounded text-[11px] flex items-center gap-1 border transition-colors ${
              showBoxes
                ? 'bg-white/10 border-white/25 text-white'
                : 'bg-transparent border-white/10 text-white/35'
            }`}
            title="Toggle Bounding Boxes"
          >
            {showBoxes ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
            Boxes
          </button>

          <button
            onClick={() => setShowLabels(!showLabels)}
            className={`px-2 py-1 rounded text-[11px] flex items-center gap-1 border transition-colors ${
              showLabels
                ? 'bg-white/10 border-white/25 text-white'
                : 'bg-transparent border-white/10 text-white/35'
            }`}
            title="Toggle Labels"
          >
            Labels
          </button>

          <div className="h-4 w-px bg-white/10 mx-1" />

          <button
            onClick={handleZoomIn}
            className="p-1 rounded text-white/40 hover:text-white hover:bg-white/10 transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <span className="text-[10px] text-white/40 min-w-[32px] text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={handleZoomOut}
            className="p-1 rounded text-white/40 hover:text-white hover:bg-white/10 transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleReset}
            className="p-1 rounded text-white/40 hover:text-white hover:bg-white/10 transition-colors"
            title="Reset View"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleFit}
            className="p-1 rounded text-white/40 hover:text-white hover:bg-white/10 transition-colors"
            title="Fit to Screen"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Interactive Sonar Canvas Viewport */}
      <div
        ref={containerRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onWheel={handleWheel}
        className="flex-1 relative overflow-hidden bg-[#040814] cursor-crosshair-sonar select-none"
      >
        {/* Transform container for pan & zoom */}
        <div
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: 'center center',
            transition: isDragging ? 'none' : 'transform 0.08s ease-out',
            width: '1600px',
            height: '900px',
            position: 'absolute',
            top: '50%',
            left: '50%',
            marginTop: '-450px',
            marginLeft: '-800px',
          }}
        >
          {/* Base Sonar Image Waterfall */}
          <img
            src={scan.imageUrl}
            alt="Side Scan Sonar Swath"
            className="w-full h-full object-cover pointer-events-none select-none"
            draggable={false}
          />

          {/* Bounding Box Overlays */}
          {showBoxes &&
            detections.map((det) => {
              const [bx, by, bw, bh] = det.bbox;
              const isSelected = det.id === selectedDetectionId;
              const isHovered = det.id === hoveredDetectionId;

              const boxBorder = isSelected
                ? 'border-2 border-white bg-white/15 shadow-[0_0_12px_rgba(255,255,255,0.3)]'
                : isHovered
                ? 'border-2 border-white/60 bg-white/8'
                : 'border border-white/40 bg-white/5 hover:border-white/70';

              return (
                <div
                  key={det.id}
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectDetection(det.id);
                  }}
                  onMouseEnter={() => setHoveredDetectionId(det.id)}
                  onMouseLeave={() => setHoveredDetectionId(null)}
                  style={{
                    position: 'absolute',
                    left: `${bx}px`,
                    top: `${by}px`,
                    width: `${bw}px`,
                    height: `${bh}px`,
                  }}
                  className={`cursor-pointer transition-all duration-150 rounded-xs ${boxBorder}`}
                >
                  {/* Caliper Corner Indicators */}
                  <div className="absolute -top-1 -left-1 w-2 h-2 border-t-2 border-l-2 border-white" />
                  <div className="absolute -top-1 -right-1 w-2 h-2 border-t-2 border-r-2 border-white" />
                  <div className="absolute -bottom-1 -left-1 w-2 h-2 border-b-2 border-l-2 border-white" />
                  <div className="absolute -bottom-1 -right-1 w-2 h-2 border-b-2 border-r-2 border-white" />

                  {/* Classification & Confidence Label */}
                  {showLabels && (
                    <div
                      className={`absolute -top-6 left-0 px-2 py-0.5 rounded text-[11px] font-mono whitespace-nowrap shadow-md pointer-events-none ${
                        isSelected
                          ? 'bg-white text-black font-bold z-20'
                          : 'bg-black/80 text-white/80 border border-white/20 z-10'
                      }`}
                    >
                      <span>{det.classification}</span>
                      <span className="ml-1.5 opacity-80">{Math.round(det.confidence * 100)}%</span>
                    </div>
                  )}

                  {/* Dimensions badge inside box if selected */}
                  {isSelected && (
                    <div className="absolute bottom-1 right-1 px-1.5 py-0.5 rounded bg-black/80 text-[10px] font-mono text-white border border-white/20">
                      {det.dimensions.length}m × {det.dimensions.width}m
                    </div>
                  )}
                </div>
              );
            })}
        </div>

        {/* Viewport HUD Overlays */}
        <div className="absolute top-3 left-3 bg-black/70 border border-white/10 rounded p-2 text-[10px] font-mono text-white/60 pointer-events-none space-y-0.5 backdrop-blur-xs">
          <div>TRANSECT: {scan.surveyName.substring(0, 24)}...</div>
          <div>SWATH ALT: {scan.altitudeMeters}m | RANGE: {scan.rangeMeters}m</div>
          <div className="text-white font-bold">
            {detections.length} ANOMALIES MAPPED
          </div>
        </div>

        <div className="absolute bottom-3 right-3 bg-black/70 border border-white/10 rounded px-2.5 py-1 text-[10px] font-mono text-white/50 pointer-events-none backdrop-blur-xs">
          Drag to Pan • Scroll to Zoom
        </div>
      </div>
    </div>
  );
};
