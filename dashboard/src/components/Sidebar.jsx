import React from 'react';

export default function Sidebar({ view, scene, grid, layers, toggle, selected, onSelect }) {
  const flagged = grid.cells.filter(d => d.label === 1);
  const flaggedAcres = flagged.length * scene.pixel_area_m2 / 4046.8564;
  const active = selected?.id ?? -1;
  const next = flagged.find(d => d.id > active) || flagged[0];
  return <aside>
    <section className="summary" hidden={view !== 'field-map' && view !== 'field-summary'}>
      <div className="kicker">FIELD SUMMARY</div>
      <h2>Stress coverage</h2>
      <div className="big">{(100*flagged.length/grid.cells.length).toFixed(2)}<small>%</small></div>
      <div className="meter"><span style={{width: (100*flagged.length/grid.cells.length)+'%'}} /></div>
      <p>{flagged.length} flagged pixels · {flaggedAcres.toFixed(2)} acres</p>
      <div className="legend"><span><i className="healthy"/>Healthy</span><span><i className="stressed"/>Stressed</span></div>
      {view === 'field-summary' && <dl className="coverage-counts">
        <div><dt>Healthy pixels</dt><dd>{grid.cells.length - flagged.length}</dd></div>
        <div><dt>Stressed pixels</dt><dd>{flagged.length}</dd></div>
        <div><dt>Total surveyed area</dt><dd>{(grid.cells.length * scene.pixel_area_m2 / 4046.8564).toFixed(2)} acres</dd></div>
      </dl>}
    </section>
    <section hidden={view !== 'field-map' && view !== 'map-layers'}><h2>Map layers</h2>
      {Object.entries({image:'Spectral composite',stress:'Stress grid',boundary:'Farm boundary'}).map(([key,label]) =>
        <label className="layer" key={key}><span>{label}</span><input type="checkbox" checked={layers[key]} onChange={() => toggle(key)}/></label>)}
    </section>
    <section hidden={view !== 'field-map' && view !== 'pixel-inspector'}><h2>Pixel inspector</h2>
      {selected ? <div aria-live="polite"><strong className={selected.label ? 'alert' : ''}>{selected.label ? 'Stressed' : 'Healthy'}</strong>
        <p>Row {selected.row} · Column {selected.col}<br/>{selected.center[1].toFixed(6)}° N, {selected.center[0].toFixed(6)}° E</p></div>
        : <p>Select a cell on the map to inspect its label and coordinates.</p>}
      {next && <button className="inspect" onClick={() => onSelect(next)}>{selected ? 'Next flagged pixel' : 'Inspect flagged pixel'}</button>}
    </section>
  </aside>;
}
