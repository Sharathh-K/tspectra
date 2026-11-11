import { useEffect, useState } from "react";

type Sample = {label: string; source: string; image: string; mean: number[]};
export default function SpectralExplorer() {
  const [samples, setSamples] = useState<Sample[]>([]);
  const [selected, setSelected] = useState(0);
  const [band, setBand] = useState(60);
  const [error, setError] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    fetch("/explorer/samples.json", {signal: controller.signal})
      .then(r => { if (!r.ok) throw new Error(); return r.json(); })
      .then(data => setSamples(data.samples))
      .catch(e => { if (e.name !== "AbortError") setError("Sample previews are unavailable."); });
    return () => controller.abort();
  }, []);
  const sample = samples[selected];
  // All samples share one axis scale, so switching samples is a fair visual comparison.
  const max = Math.max(1, ...samples.flatMap(s => s.mean));
  const points = sample?.mean.map((v, i) => `${45+i*4},${180-150*v/max}`).join(" ");
  return <section className="info-card spectral-explorer">
    <span className="eyebrow">REAL DATA EXPLORER</span>
    <h2>Look inside a hyperspectral patch</h2>
    <p>Choose an example to see its false-colour preview and average signal across 125 bands. Labels come from the dataset folders.</p>
    {error && <p role="alert">{error}</p>}
    {!sample && !error && <p role="status">Loading samples…</p>}
    {sample && <>
      <label>Dataset example <select value={selected} onChange={e => setSelected(Number(e.target.value))}>
        {samples.map((s, i) => <option key={s.source} value={i}>{s.label} · example {i%2+1}</option>)}
      </select></label>
      <div className="spectral-layout">
        <figure><img className="sample-preview" src={sample.image} alt={`False-colour 64 by 64 patch labelled ${sample.label}`} />
          <figcaption>{sample.source}<br />Bands 90 / 60 / 30 → RGB</figcaption></figure>
        <div>
          <svg viewBox="0 0 560 220" role="img" aria-label={`Mean sensor signal across 125 bands for ${sample.source}`}>
            <path d="M45 20 V180 H541" fill="none" stroke="#92a894" />
            <polyline points={points} fill="none" stroke="#b9ea8c" strokeWidth="2" />
            <circle cx={45+(band-1)*4} cy={180-150*sample.mean[band-1]/max} r="4" fill="#edbb53" />
            <text x="45" y="15" fill="currentColor" fontSize="11">Mean sensor value (0–{Math.ceil(max)})</text>
            <text x="45" y="200" fill="currentColor" fontSize="11">1</text>
            <text x="250" y="210" fill="currentColor" fontSize="11">Band index</text>
            <text x="520" y="200" fill="currentColor" fontSize="11">125</text>
          </svg>
          <label>Inspect band <input type="range" min="1" max="125" value={band} onChange={e => setBand(Number(e.target.value))} /></label>
          <p aria-live="polite">Band {band}: <strong>{sample.mean[band-1].toFixed(1)}</strong> mean sensor units.</p>
        </div>
      </div>
      <p>Colours are stretched independently for visibility; pink does not mean disease. The curve averages all pixels, including background. Sensor units are not calibrated reflectance, and band indices are not wavelengths in nanometres.</p>
    </>}
  </section>;
}
