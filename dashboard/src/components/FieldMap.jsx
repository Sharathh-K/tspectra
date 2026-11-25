import React, { useMemo, useState } from 'react';
import DeckGL from '@deck.gl/react';
import { WebMercatorViewport } from '@deck.gl/core';
import MapboxMap from 'react-map-gl/mapbox';
import 'mapbox-gl/dist/mapbox-gl.css';
import { farmLayers } from '../layers/farm';

const token = import.meta.env.VITE_MAPBOX_TOKEN;

function homeCamera(grid, width, height) {
  const xs = grid.boundary.map(p => p[0]), ys = grid.boundary.map(p => p[1]);
  const bounds = [[Math.min(...xs), Math.min(...ys)], [Math.max(...xs), Math.max(...ys)]];
  const vp = new WebMercatorViewport({ width, height }).fitBounds(bounds, { padding: 52 });
  return { longitude: vp.longitude, latitude: vp.latitude, zoom: vp.zoom - 0.15,
    pitch: 32, bearing: -12, minZoom: 3, maxZoom: 21 };
}

export default function FieldMap({ scene, grid, layers, selected, onSelect }) {
  const [size, setSize] = useState([560, 520]);
  const [position, setPosition] = useState(null);
  const [baseError, setBaseError] = useState(false);
  const home = useMemo(() => homeCamera(grid, ...size), [grid, size]);
  const camera = position || home;
  const mapLayers = useMemo(() => farmLayers(scene, grid, layers, selected, onSelect),
    [scene, grid, layers, selected, onSelect]);
  return <section className="map" aria-label="Interactive farm map">
    <DeckGL viewState={camera} onViewStateChange={({viewState}) => setPosition(viewState)}
      onResize={({width,height}) => { if (width > 120 && height > 120) setSize([width,height]); }}
      controller layers={mapLayers} getCursor={({isDragging,isHovering}) => isDragging ? 'grabbing' : isHovering ? 'crosshair' : 'grab'}>
      {token && !baseError && <MapboxMap mapboxAccessToken={token} reuseMaps
        mapStyle="mapbox://styles/mapbox/satellite-streets-v12" projection="mercator"
        onError={event => { if ([401,403].includes(event.error?.status)) setBaseError(true); }} />}
    </DeckGL>
    <div className="map-tag"><span className="cross">⌖</span> {token && !baseError ? 'Satellite basemap' : 'Local raster map'}</div>
    <div className="map-controls">
      <button aria-label="Zoom in" onClick={() => setPosition({...camera, zoom: Math.min(21,camera.zoom+1)})}>+</button>
      <button aria-label="Zoom out" onClick={() => setPosition({...camera, zoom: Math.max(3,camera.zoom-1)})}>−</button>
      <button onClick={() => setPosition({...camera, pitch: camera.pitch > 0 ? 0 : 40})}>{camera.pitch > 0 ? '2D' : '3D'}</button>
      <button onClick={() => setPosition(null)}>Fit</button>
    </div>
    <div className="map-bottom"><span>{camera.latitude.toFixed(4)}° N · {camera.longitude.toFixed(4)}° E</span><span>WGS 84</span></div>
  </section>;
}
