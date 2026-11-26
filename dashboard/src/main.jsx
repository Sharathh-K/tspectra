import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { useRiskData } from './hooks/useRiskData';
import { geometry } from './layers/geometry';
import FieldMap from './components/FieldMap';
import Navigation, { destinations } from './components/Navigation';
import Sidebar from './components/Sidebar';
import './styles.css';

function currentView() {
  return destinations.find(([id]) => id === window.location.hash.slice(1)) || destinations[0];
}

function App() {
  const [[view, title], setView] = useState(currentView);
  useEffect(() => {
    const navigate = () => {
      setView(currentView());
      window.scrollTo(0, 0);
      document.getElementById('view-heading')?.focus({preventScroll:true});
    };
    window.addEventListener('hashchange', navigate);
    return () => window.removeEventListener('hashchange', navigate);
  }, []);
  const { scene, error, retry } = useRiskData();
  const grid = useMemo(() => scene && geometry(scene), [scene]);
  const [layers, setLayers] = useState({image:true, stress:true, boundary:true});
  const [selected, onSelect] = useState(null);

  return <div className="app-shell">
    <Navigation active={view} ready={Boolean(scene && !error)}/>
    <main>
      <div className="heading">
        <div><div className="kicker">FIELD OPERATIONS</div><h1 id="view-heading" tabIndex={-1}>{title}</h1></div>
        {scene && <div className="acq">Mock acquisition
          <b>{new Date(scene.date + 'T12:00:00Z').toLocaleDateString('en-GB', {
            day:'numeric', month:'short', year:'numeric', timeZone:'UTC'
          })}</b>
        </div>}
      </div>
      {error ? <p role="alert">{error} <button onClick={retry}>Retry</button></p> :
        !scene ? <p role="status">Loading field…</p> : <>
          <div className="workspace" data-view={view}>
            <section className="map-card" hidden={view === 'field-summary'} aria-label="Field map">
              <div className="map-heading">
                <div><div className="kicker">FIELD MAP</div><h2>{scene.field}</h2></div>
                <span className="pill">Synthetic scene</span>
              </div>
              <FieldMap {...{scene, grid, layers, selected, onSelect}}/>
            </section>
            <Sidebar view={view} {...{scene, grid, layers, selected, onSelect}}
              toggle={key => setLayers(prev => ({...prev, [key]:!prev[key]}))}/>
          </div>
          <footer>{[[scene.width+' × '+scene.height,'Raster grid'],[Math.sqrt(scene.pixel_area_m2)+' m','Pixel resolution'],
            [scene.band_count,'Spectral bands'],[scene.source_crs,'Source projection']].map(([value,label]) =>
              <div key={label}><small>{label}</small><strong>{value}</strong></div>)}</footer>
        </>}
    </main>
  </div>;
}
createRoot(document.getElementById('root')).render(<App/>);
