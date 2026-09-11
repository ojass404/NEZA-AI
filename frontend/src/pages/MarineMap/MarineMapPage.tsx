import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { useAppState } from '../../context/AppStateContext';
import { Detection } from '../../models/types';
import { PriorityBadge, VerificationBadge, ConfidenceBadge, DemoBadge } from '../../components/common/Badges';
import { Filter, ZoomIn, ZoomOut, RotateCcw, ArrowRight } from 'lucide-react';

const DEMO_OCEAN_CENTER: [number, number] = [79.1891, 9.1558];

export const MarineMapPage: React.FC = () => {
  const navigate = useNavigate();
  const { geojson, detections, scans, mapFilters, setMapFilters, setSelectedDetectionId } = useAppState();

  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);

  const [mapReady, setMapReady] = useState(false);
  const [selectedMapDetection, setSelectedMapDetection] = useState<Detection | null>(null);
  const [mapStyle, setMapStyle] = useState<'voyager' | 'ocean-dark' | 'hydro'>('hydro');

  const filteredDetections = detections.filter((det) => {
    if (mapFilters.survey !== 'ALL' && det.scanId !== mapFilters.survey) return false;
    if (mapFilters.priority !== 'ALL' && det.priority !== mapFilters.priority) return false;
    if (mapFilters.verification !== 'ALL' && det.verificationStatus !== mapFilters.verification) return false;
    if (mapFilters.classification !== 'ALL' && !det.classification.includes(mapFilters.classification)) return false;
    return true;
  });

  useEffect(() => {
    if (!mapContainerRef.current) return;

    const tileSources = {
      voyager: 'https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
      'ocean-dark': 'https://basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}{r}.png',
      hydro: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    };

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: {
        version: 8,
        sources: {
          'raster-tiles': {
            type: 'raster',
            tiles: [tileSources[mapStyle]],
            tileSize: 256,
            attribution: '© OpenStreetMap © CARTO',
          },
        },
        layers: [
          {
            id: 'simple-tiles',
            type: 'raster',
            source: 'raster-tiles',
            minzoom: 0,
            maxzoom: 19,
          },
        ],
      },
      center: DEMO_OCEAN_CENTER,
      zoom: 7,
    });

    mapRef.current = map;
    setMapReady(false);
    map.on('style.load', () => setMapReady(true));
    if (map.getLayer('simple-tiles')) setMapReady(true);

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, [mapStyle]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    const allowed = new Set(filteredDetections.map(d => d.id));
    const data = {...geojson, features: geojson.features.filter((f: any) => allowed.has(f.id))};
    const update = () => {
      const source = map.getSource('detections') as maplibregl.GeoJSONSource | undefined;
      if (source) source.setData(data);
      else {
        map.addSource('detections', {type: 'geojson', data, generateId: true});
        map.addLayer({id: 'detections', type: 'circle', source: 'detections', paint: {'circle-radius': 8, 'circle-color': '#E8AF30', 'circle-stroke-width': 2, 'circle-stroke-color': ['case', ['==', ['get', 'verification_status'], 'CONFIRMED'], '#16A34A', '#ffffff']}});
      }
      if (data.features.length) {
        const bounds = new maplibregl.LngLatBounds();
        data.features.forEach((f: any) => bounds.extend(f.geometry.coordinates));
        map.fitBounds(bounds, {padding: 70, maxZoom: 12});
      }
    };
    const select = (event: any) => {
      const id = event.features?.[0]?.properties?.detection_id;
      setSelectedMapDetection(detections.find(d => d.id === String(id)) || null);
    };
    if (map.getLayer('simple-tiles')) update(); else map.once('style.load', update);
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = data.features.map((feature: any) => {
      const button = document.createElement('button');
      button.setAttribute('aria-label', `Map candidate ${feature.properties.detection_id}`);
      button.style.cssText = 'width:20px;height:20px;border-radius:50%;background:#E8AF30;border:3px solid #16A34A;box-shadow:0 0 0 3px #0008;cursor:pointer';
      if (feature.properties.verification_status !== 'CONFIRMED') button.style.borderColor = '#ffffff';
      button.onclick = () => setSelectedMapDetection(detections.find(d => d.id === feature.properties.detection_id) || null);
      return new maplibregl.Marker({element: button}).setLngLat(feature.geometry.coordinates).addTo(map);
    });

    map.on('click', 'detections', select);
    return () => { map.off('style.load', update); map.off('click', 'detections', select); markersRef.current.forEach(marker => marker.remove()); };
  }, [geojson, detections, mapFilters, mapStyle, mapReady]);

  const handleResetView = () => {
    mapRef.current?.flyTo({ center: DEMO_OCEAN_CENTER, zoom: 7 });
    setSelectedMapDetection(null);
  };

  const handleOpenDetails = (det: Detection) => {
    setSelectedDetectionId(det.id);
    navigate(`/detection/${det.id}`);
  };

  return (
    <div className="space-y-4 animate-fade-in relative">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl md:text-2xl font-extrabold text-white tracking-tight">
              Geospatial Marine Map
            </h1>
            <DemoBadge text="FRAME-LEVEL GPS" />
          </div>
          <p className="text-xs text-white/40 mt-0.5">
            Georeferenced spatial distribution of sonar anomalies across surveyed marine sectors.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-white/40 text-[11px]">Layer:</span>
          <select
            value={mapStyle}
            onChange={(e) => setMapStyle(e.target.value as any)}
            className="bg-[#1e1e1e] border border-white/10 rounded-lg px-2.5 py-1 text-xs text-white/70 font-semibold focus:outline-hidden"
          >
            <option value="voyager">Standard Nautical (Light)</option>
            <option value="ocean-dark">Hydrographic Dark</option>
            <option value="hydro">OpenStreetMap</option>
          </select>
        </div>
      </div>

      <div className="bg-[#161616] border border-white/8 rounded-xl p-3.5 flex flex-wrap items-center gap-3 text-xs font-mono">
        <div className="flex items-center gap-1.5 text-white/60 font-bold">
          <Filter className="w-3.5 h-3.5" />
          <span>FILTERS:</span>
        </div>

        <select
          value={mapFilters.survey}
          onChange={(e) => setMapFilters((prev) => ({ ...prev, survey: e.target.value }))}
          className="bg-[#1e1e1e] border border-white/10 rounded-lg px-2.5 py-1 text-white/70 font-semibold focus:outline-hidden"
        >
          <option value="ALL">All Surveys</option>
          {scans.map((s) => (
            <option key={s.id} value={s.id}>
              {s.id}: {s.surveyName.substring(0, 24)}...
            </option>
          ))}
        </select>

        <select
          value={mapFilters.priority}
          onChange={(e) => setMapFilters((prev) => ({ ...prev, priority: e.target.value }))}
          className="bg-[#1e1e1e] border border-white/10 rounded-lg px-2.5 py-1 text-white/70 font-semibold focus:outline-hidden"
        >
          <option value="ALL">All Priorities</option>
          <option value="HIGH">HIGH Priority</option>
          <option value="MEDIUM">MEDIUM Priority</option>
          <option value="LOW">LOW Priority</option>
        </select>

        <select
          value={mapFilters.verification}
          onChange={(e) => setMapFilters((prev) => ({ ...prev, verification: e.target.value }))}
          className="bg-[#1e1e1e] border border-white/10 rounded-lg px-2.5 py-1 text-white/70 font-semibold focus:outline-hidden"
        >
          <option value="ALL">All Verification States</option>
          <option value="PENDING">Pending Review</option>
          <option value="CONFIRMED">Human Verified</option>
          <option value="REJECTED">Rejected</option>
        </select>

        <button
          onClick={() => setMapFilters({ survey: 'ALL', classification: 'ALL', priority: 'ALL', verification: 'ALL' })}
          className="ml-auto text-[11px] text-white/40 font-semibold hover:text-white transition-colors"
        >
          Reset Filters
        </button>
      </div>

      <div className="text-xs text-white/60">{geojson.features.length} geotagged candidates. Explicit or selected demo frame GPS is plotted.
        {filteredDetections.filter(d => d.latitude !== null && d.longitude !== null).map(d => <button key={d.id} className="ml-3 underline" onClick={() => {setSelectedMapDetection(d); mapRef.current?.flyTo({center: [d.longitude!, d.latitude!], zoom: 12});}}>Select {d.id.slice(0, 8)}</button>)}
      </div>
      <div className="relative w-full h-[620px] rounded-2xl overflow-hidden border border-white/10 shadow-md bg-[#0d0d0d]">
        <div ref={mapContainerRef} className="w-full h-full" />

        <div className="absolute top-4 right-4 flex flex-col gap-1.5 z-10">
          <button
            onClick={() => mapRef.current?.zoomIn()}
            className="p-2 bg-[#161616]/95 border border-white/10 rounded-xl text-white/70 hover:bg-white/10 transition-all shadow-md"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={() => mapRef.current?.zoomOut()}
            className="p-2 bg-[#161616]/95 border border-white/10 rounded-xl text-white/70 hover:bg-white/10 transition-all shadow-md"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={handleResetView}
            className="p-2 bg-[#161616]/95 border border-white/10 rounded-xl text-white/70 hover:bg-white/10 transition-all shadow-md"
            title="Reset Sector View"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>

        <div className="absolute bottom-4 left-4 bg-[#161616]/95 border border-white/10 rounded-xl p-3.5 z-10 text-[11px] font-mono text-white shadow-lg backdrop-blur-xs">
          <span className="font-bold text-white/60 block mb-1.5 uppercase">Priority Legend</span>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-white inline-block border border-white/50" />
              <span className="text-white/70">HIGH review priority</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-white/50 inline-block border border-white/30" />
              <span className="text-white/70">MEDIUM review priority</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-white/20 inline-block border border-white/15" />
              <span className="text-white/70">LOW review priority</span>
            </div>
          </div>
          <div className="pt-2 mt-2 border-t border-white/8 text-[10px] text-white/30">
            Green Border = Verified by Human Analyst
          </div>
        </div>

        {selectedMapDetection && (
          <div className="absolute top-4 left-4 max-w-sm w-full bg-[#161616]/98 border border-white/10 rounded-2xl p-4 shadow-xl z-10 text-white backdrop-blur-sm animate-fade-in">
            <div className="flex items-start justify-between mb-2">
              <div>
                <span className="font-mono text-xs font-bold text-white/50 block">
                  {selectedMapDetection.id}
                </span>
                <h4 className="text-sm font-bold text-white">
                  {selectedMapDetection.classification}
                </h4>
              </div>
              <button
                onClick={() => setSelectedMapDetection(null)}
                className="text-white/30 hover:text-white/60 text-xs font-mono transition-colors"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2 my-2 text-xs font-mono">
              <div>
                <span className="text-[10px] text-white/30 block">CONFIDENCE</span>
                <ConfidenceBadge confidence={selectedMapDetection.confidence} />
              </div>
              <div>
                <span className="text-[10px] text-white/30 block">PRIORITY</span>
                <PriorityBadge priority={selectedMapDetection.priority} />
              </div>
            </div>

            <div className="my-2 p-2.5 bg-[#1e1e1e] rounded-xl border border-white/8 text-[11px] font-mono space-y-1">
              <div className="flex justify-between">
                <span className="text-white/40">Depth:</span>
                <span className="font-bold text-white">{selectedMapDetection.depth} m</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/40">Coordinates:</span>
                <span className="text-white/70 font-semibold">
                  {selectedMapDetection.latitude?.toFixed(4)}°, {selectedMapDetection.longitude?.toFixed(4)}°
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/40">Verification:</span>
                <VerificationBadge status={selectedMapDetection.verificationStatus} />
              </div>
            </div>

            <button
              onClick={() => handleOpenDetails(selectedMapDetection)}
              className="w-full mt-2 py-2 px-3 rounded-xl bg-white text-black font-bold text-xs font-mono flex items-center justify-center gap-1.5 transition-all hover:bg-white/90"
            >
              <span>Inspect Anomaly Details</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
