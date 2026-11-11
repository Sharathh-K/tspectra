export default function DashboardGuide() {
  return <div className="guide-stack">
    <section className="info-card">
      <span className="eyebrow">QUICK START</span><h2>Follow an image through TerraSpectra</h2>
      <p>Start with data, inspect the model evidence, then try inference. Explore the simulated farm separately to learn how a geographic dashboard behaves.</p>
      <a className="text-link" href="/dashboard-guide.md" download>Download the complete dashboard guide (.md) ↓</a>
    </section>
    {[
      ["data", "1. Understand the data", "Choose Health, Other or Rust in the spectral explorer. Move the band slider to inspect the patch’s average signal. The 125 measurements are compressed into 16 PCA components before classification."],
      ["models", "2. Read the evidence", "The transformer correctly classified 85 of 120 development examples. That is 70.8% accuracy on this split—not a 70.8% guarantee for a new farm. Compare class recall too: improved overall accuracy did not improve every class."],
      ["inference", "3. Classify a compatible image", "Choose a 64 × 64 TIFF from the original dataset and use patch mode. For larger compatible rasters, choose tiled mode and download the ZIP. A Rust score is a model class score, not a confirmed diagnosis or time-to-outbreak estimate."],
      ["map", "4. Explore the demonstration farm", "Select a cell, change the minimum score and move the timeline. A threshold of 0 includes all 80 cells. Raising it selects fewer cells and changes the displayed acreage. Opacity changes appearance, not scores. The four stages are invented examples, not dated observations."],
    ].map(([route, title, description]) => <section className="info-card" key={route}><h2>{title}</h2><p>{description}</p><a className="text-link" href={`#/${route}`}>Open workspace →</a></section>)}
    <section className="info-card"><h2>What the platform can establish</h2>
      <p>Real evidence: dataset preparation, saved model classification results, CPU inference and bounded tiling. Simulation: farm scores, acreage and timeline. Not established: chemical deficiencies, real farm GPS disease maps, three-week forecasting or GPU throughput.</p>
      <h3>Need help?</h3><p>No satellite tiles? Use the diagram, or configure your public Mapbox token. Inference unavailable? Start the local API and use “Check service.” Unsupported TIFF? Select an original compatible dataset TIFF; RGB pictures and arbitrary 224-band cubes cannot use this saved model.</p>
      <p>Changing pages resets local form and map selections. Keep a downloaded result before leaving the page.</p>
    </section>
  </div>;
}
