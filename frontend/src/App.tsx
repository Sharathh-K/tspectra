import { useEffect, useState } from "react";
import FarmMap from "./FarmMap";
import ModelResults from "./ModelResults";
import InferencePanel from "./InferencePanel";
import WeekThreeResults from "./WeekThreeResults";
import MidReview from "./MidReview";

type Summary = {
  files: number;
  shape_hwb: number[];
  pca_components: number;
  splits: Record<string, number>;
  retained_variance: number;
};

export default function App() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    fetch("/dataset-summary.json")
      .then((response) => {
        if (!response.ok)
          throw new Error(
            "Run the preparation command to create the dataset summary.",
          );
        return response.json();
      })
      .then(setSummary)
      .catch(() =>
        setError(
          "Dataset summary unavailable. Run the Python preparation command.",
        ),
      );
  }, []);
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#overview">
          <span className="brand-icon">◈</span> TerraSpectra
          <span className="brand-dot">.</span>
        </a>
        <div className="workspace">AGRICULTURE WORKSPACE</div>
        <nav aria-label="Main navigation">
          <a href="#inference">
            ⇧ <span>Inference</span>
          </a>
          <a href="#model-comparison">
            ◈ <span>Model comparison</span>
          </a>
          <a href="#analytics">
            ▥ <span>Analytics</span>
          </a>
          <a href="#data-quality">
            ✓ <span>Data quality</span>
          </a>
          <a className="active" href="#overview">
            ◫ <span>Farm overview</span>
            <span>↗</span>
          </a>
          <a href="#preparation">
            ≋ <span>Data preparation</span>
          </a>
          <a href="#model-results">
            ☷ <span>Model results</span>
          </a>
        </nav>
        <div className="sidebar-note">
          <span className="eyebrow">THE NEXT STEP</span>
          <h3>
            Teach the model.
            <br />
            Explore the heatmap.
          </h3>
          <p>
            A compact classifier and an honest simulation of a farm overlay.
          </p>
        </div>
        <div className="sidebar-footer">
          <span className="status-dot" /> Crop health analytics
        </div>
      </aside>
      <main id="overview">
        <header>
          <div>
            <span className="eyebrow">
              PRECISION AGRICULTURE / TERRASPECTRA
            </span>
            <h1>A clearer view of crop health.</h1>
            <p>
              A compact disease classifier & an interactive simulated heatmap.
            </p>
          </div>
          <span className="week-badge">
            EXPLORER <span>Models & maps</span>
          </span>
        </header>
        <section className="metrics" aria-label="Dataset overview">
          {[
            ["IMAGE PATCHES", summary?.files, "Kaggle competition files"],
            ["SPECTRAL BANDS", summary?.shape_hwb[2], "Measurements per pixel"],
            [
              "PCA COMPONENTS",
              summary?.pca_components,
              "Compact spectral representation",
            ],
          ].map(([label, value, detail]) => (
            <article className="metric" key={String(label)}>
              <span className="eyebrow">{label}</span>
              <strong>{value ?? "—"}</strong>
              <span>{detail}</span>
            </article>
          ))}
        </section>
        {error && (
          <p role="alert" className="notice">
            {error}
          </p>
        )}
        <section className="map-heading">
          <div>
            <span className="eyebrow">GEOGRAPHIC WORKSPACE</span>
            <h2>Simulated farm heatmap</h2>
          </div>
          <span className="demo-badge">SIMULATED DATA</span>
        </section>
        <FarmMap />
        <p className="map-caption">
          Demonstration location near Bengaluru · Scores and cell coordinates
          are invented for UI development. They are not model predictions,
          infected pixels or measured farm risk.
        </p>
        <InferencePanel />
        <WeekThreeResults />
        <ModelResults />
        <MidReview />
        <div className="lower-grid">
          <section className="info-card" id="preparation">
            <span className="eyebrow">DATA PREPARATION</span>
            <h2>From many bands to useful patterns.</h2>
            <p>
              Think of each image as a stack of 125 transparent pages. PCA makes
              16 new pages that preserve much of the variation.
            </p>
            <div className="pipeline">
              <span>TIFF cubes</span>
              <b>→</b>
              <span>Scale bands</span>
              <b>→</b>
              <span>16 components</span>
            </div>
            <dl>
              <div>
                <dt>Training images</dt>
                <dd>{summary?.splits.train ?? "—"}</dd>
              </div>
              <div>
                <dt>Development validation</dt>
                <dd>{summary?.splits.validation ?? "—"}</dd>
              </div>
              <div>
                <dt>Unlabelled inference images</dt>
                <dd>{summary?.splits.unlabelled ?? "—"}</dd>
              </div>
            </dl>
            <small>
              PCA learns from training images only. Retained variance:{" "}
              {summary
                ? `${(summary.retained_variance * 100).toFixed(1)}%`
                : "—"}
              . This is not disease accuracy.
            </small>
          </section>
          <section className="info-card" id="capabilities">
            <span className="eyebrow">EXPLORE THE PLATFORM</span>
            <h2>Classification and visualization.</h2>
            <ul className="checklist">
              <li>Classify compatible hyperspectral patches</li>
              <li>Compare model performance</li>
              <li>Explore the simulated farm grid</li>
              <li>Inspect cells, filter scores and adjust opacity</li>
            </ul>
          </section>
        </div>
        <footer>
          TerraSpectra · Crop health analytics{" "}
          <span>Data first. Clear assumptions. Measurable progress.</span>
        </footer>
      </main>
    </div>
  );
}
