import {useEffect, useState} from 'react';
import FarmMap from './FarmMap';

type Summary = {files: number; shape_hwb: number[]; pca_components: number;
  splits: Record<string, number>; retained_variance: number};

export default function App() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    fetch('/dataset-summary.json').then(response => {
      if (!response.ok) throw new Error('Run the preparation command to create the dataset summary.');
      return response.json();
    }).then(setSummary).catch(() => setError('Dataset summary unavailable. Run the Python preparation command.'));
  }, []);
  return <div className="app-shell">
    <aside className="sidebar">
      <a className="brand" href="#overview"><span className="brand-icon">◈</span> TerraSpectra<span className="brand-dot">.</span></a>
      <div className="workspace">INTERNSHIP WORKSPACE <span>01</span></div>
      <nav aria-label="Main navigation"><a className="active" href="#overview">◫ <span>Farm overview</span><span>↗</span></a><a href="#preparation">≋ <span>Data preparation</span></a><a href="#week-one">☷ <span>Week 1 checklist</span></a></nav>
      <div className="sidebar-note"><span className="eyebrow">THE FOUNDATION</span><h3>Understand the data.<br/>Build the map.</h3><p>A small, clear first step towards hyperspectral crop monitoring.</p></div>
      <div className="sidebar-footer"><span className="status-dot" /> Week 1 · Development</div>
    </aside>
    <main id="overview">
      <header><div><span className="eyebrow">PRECISION AGRICULTURE / TERRASPECTRA</span><h1>A clearer view of crop health.</h1><p>Hyperspectral data preparation & geographic map foundations.</p></div><span className="week-badge">WEEK 01 <span>Foundation</span></span></header>
      <section className="metrics" aria-label="Dataset overview">
        {[['IMAGE PATCHES', summary?.files, 'Kaggle competition files'],
          ['SPECTRAL BANDS', summary?.shape_hwb[2], 'Measurements per pixel'],
          ['PCA COMPONENTS', summary?.pca_components, 'Compact spectral representation']].map(([label, value, detail]) =>
          <article className="metric" key={String(label)}><span className="eyebrow">{label}</span><strong>{value ?? '—'}</strong><span>{detail}</span></article>)}
      </section>
      {error && <p role="alert" className="notice">{error}</p>}
      <section className="map-heading"><div><span className="eyebrow">GEOGRAPHIC WORKSPACE</span><h2>Farm overview</h2></div><span className="demo-badge">SYNTHETIC BOUNDARY</span></section>
      <FarmMap />
      <p className="map-caption">Demonstration location near Bengaluru · This boundary is independent of the Kaggle image patches. Disease predictions are not available in Week 1.</p>
      <div className="lower-grid"><section className="info-card" id="preparation"><span className="eyebrow">DATA PREPARATION</span><h2>From many bands to useful patterns.</h2><p>Think of each image as a stack of 125 transparent pages. PCA makes 16 new pages that preserve much of the variation.</p>
        <div className="pipeline"><span>TIFF cubes</span><b>→</b><span>Scale bands</span><b>→</b><span>16 components</span></div>
        <dl><div><dt>Training images</dt><dd>{summary?.splits.train ?? '—'}</dd></div><div><dt>Development validation</dt><dd>{summary?.splits.validation ?? '—'}</dd></div><div><dt>Unlabelled inference images</dt><dd>{summary?.splits.unlabelled ?? '—'}</dd></div></dl>
        <small>PCA learns from training images only. Retained variance: {summary ? `${(summary.retained_variance * 100).toFixed(1)}%` : '—'}. This is not disease accuracy.</small>
      </section><section className="info-card" id="week-one"><span className="eyebrow">WEEK 1 SCOPE</span><h2>The groundwork.</h2><ul className="checklist"><li>Read and inspect hyperspectral TIFFs</li><li>Preserve labels and build a file inventory</li><li>Fit and save a reusable PCA pipeline</li><li>Connect Mapbox with a Deck.gl farm layer</li></ul><p className="next-step">UP NEXT <span>Week 2 · Disease classification model</span></p></section></div>
      <footer>TerraSpectra · Internship project <span>Data first. Clear assumptions. Measurable progress.</span></footer>
    </main>
  </div>;
}
