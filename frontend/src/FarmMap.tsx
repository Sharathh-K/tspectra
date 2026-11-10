import {useEffect, useRef, useState} from 'react';
import mapboxgl from 'mapbox-gl';
import {MapboxOverlay} from '@deck.gl/mapbox';
import {GeoJsonLayer} from '@deck.gl/layers';
import {demoFarm, FARM_CENTER} from './farm';

export default function FarmMap() {
  const container = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const overlay = useRef<MapboxOverlay | null>(null);
  const [showBoundary, setShowBoundary] = useState(true);
  const [status, setStatus] = useState('Loading satellite map…');
  const token = import.meta.env.VITE_MAPBOX_TOKEN;
  const hasToken = Boolean(token && !token.includes('your_public_token'));

  useEffect(() => {
    if (!hasToken || !container.current) return;
    const instance = new mapboxgl.Map({
      container: container.current, accessToken: token,
      style: 'mapbox://styles/mapbox/satellite-streets-v12',
      center: FARM_CENTER, zoom: 14, pitch: 45, bearing: -15
    });
    map.current = instance;
    instance.addControl(new mapboxgl.NavigationControl(), 'top-right');
    const deck = new MapboxOverlay({interleaved: false, layers: []});
    overlay.current = deck;
    instance.addControl(deck);
    instance.on('load', () => setStatus('Satellite basemap ready'));
    instance.on('error', () => setStatus('Map unavailable. Check your public token and internet connection.'));
    // React may mount twice in development. Always clean up the old map.
    return () => {instance.remove(); map.current = null; overlay.current = null;};
  }, [hasToken, token]);

  useEffect(() => {
    overlay.current?.setProps({layers: [new GeoJsonLayer({
      id: 'demo-farm-boundary', data: demoFarm, visible: showBoundary,
      filled: true, stroked: true, getFillColor: [127, 224, 165, 35],
      getLineColor: [167, 242, 112, 255], getLineWidth: 3, lineWidthUnits: 'pixels',
      pickable: false
    })]});
  }, [showBoundary, hasToken, token]);

  function resetView() {
    map.current?.flyTo({center: FARM_CENTER, zoom: 14, pitch: 45, bearing: -15});
  }

  return <section className="map-panel" aria-label="Demonstration farm map">
    <div ref={container} className="map-canvas" />
    {!hasToken && <div className="map-placeholder">
      <div className="coordinate-grid" />
      <div className="demo-outline" aria-hidden="true" />
      <div className="token-message"><span className="eyebrow">MAP SETUP</span>
        <h2>Your farm map starts here.</h2>
        <p>Add a public Mapbox token to <code>frontend/.env.local</code>, then restart the app.</p>
        <p>This grid is a setup placeholder. It is not satellite imagery.</p>
      </div>
    </div>}
    <div className="map-top"><span className="map-tag">{hasToken ? 'SATELLITE VIEW' : 'SETUP PREVIEW'}</span>
      <button onClick={resetView} disabled={!hasToken}>Reset view ↗</button></div>
    <div className="map-bottom"><label><input type="checkbox" checked={showBoundary}
      disabled={!hasToken} onChange={event => setShowBoundary(event.target.checked)} /> Demo boundary</label>
      <span>{hasToken ? status : 'Mapbox token required'}</span></div>
  </section>;
}
