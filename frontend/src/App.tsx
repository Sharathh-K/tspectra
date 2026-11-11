import { useEffect, useRef, useState } from "react";
import FarmMap from "./FarmMap";
import ModelResults from "./ModelResults";
import InferencePanel from "./InferencePanel";
import WeekThreeResults from "./WeekThreeResults";
import MidReview from "./MidReview";
import SpectralExplorer from "./SpectralExplorer";
import DashboardGuide from "./DashboardGuide";

type Summary = {
  files: number;
  shape_hwb: number[];
  pca_components: number;
  splits: Record<string, number>;
  retained_variance: number;
};

const pages = {
  overview: ["Overview", "A clearer view of crop health."],
  map: ["Map & analytics", "Explore the demonstration farm."],
  inference: ["Inference", "Classify a compatible TIFF."],
  models: ["Model performance", "Compare measured results."],
  data: ["Data quality", "Understand the data behind the model."],
  guide: ["Dashboard guide", "Your guide to the workspace."],
} as const;
type Page = keyof typeof pages;
function currentPage(): Page {
  const value = window.location.hash.replace(/^#\/?/, "");
  const aliases: Record<string, Page> = {
    preparation: "data",
    "data-quality": "data",
    "mid-review": "data",
    analytics: "map",
    "model-results": "models",
    "model-comparison": "models",
    "week-three": "models",
    "week-two": "overview",
  };
  const candidate = aliases[value] ?? value;
  return Object.keys(pages).includes(candidate)
    ? (candidate as Page)
    : "overview";
}

export default function App() {
  const [page, setPage] = useState<Page>(currentPage);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState("");
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    const navigate = () => setPage(currentPage());
    window.addEventListener("hashchange", navigate);
    return () => window.removeEventListener("hashchange", navigate);
  }, []);
  useEffect(() => {
    document.title = `TerraSpectra · ${pages[page][0]}`;
    window.scrollTo(0, 0);
    heading.current?.focus({ preventScroll: true });
  }, [page]);
  useEffect(() => {
    const controller = new AbortController();
    fetch("/dataset-summary.json", { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error();
        return response.json();
      })
      .then(setSummary)
      .catch((error) => {
        if (error.name !== "AbortError")
          setError("Dataset summary unavailable.");
      });
    return () => controller.abort();
  }, []);
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#/overview">
          <span className="brand-icon">◈</span> TerraSpectra
          <span className="brand-dot">.</span>
        </a>
        <div className="workspace">AGRICULTURE WORKSPACE</div>
        <nav aria-label="Main navigation">
          {(Object.keys(pages) as Page[]).map((key) => (
            <a
              key={key}
              href={`#/${key}`}
              className={page === key ? "active" : ""}
              aria-current={page === key ? "page" : undefined}
            >
              <span>{pages[key][0]}</span>
            </a>
          ))}
        </nav>
        <div className="sidebar-note">
          <span className="eyebrow">EXPLORE WITH CONTEXT</span>
          <h3>
            Measured models.
            <br />
            Simulated maps.
          </h3>
          <p>Patch classification and clearly labelled farm visualization.</p>
        </div>
        <div className="sidebar-footer">
          <span className="status-dot" /> Crop health analytics
        </div>
      </aside>
      <main>
        <header>
          <div>
            <span className="eyebrow">
              TERRASPECTRA / {pages[page][0].toUpperCase()}
            </span>
            <h1 ref={heading} tabIndex={-1}>
              {pages[page][1]}
            </h1>
          </div>
        </header>
        {page === "overview" && (
          <>
            <section className="metrics" aria-label="Dataset overview">
              {[
                ["IMAGE PATCHES", summary?.files],
                ["SPECTRAL BANDS", summary?.shape_hwb[2]],
                ["PCA COMPONENTS", summary?.pca_components],
              ].map(([label, value]) => (
                <article className="metric" key={String(label)}>
                  <span className="eyebrow">{label}</span>
                  <strong>{value ?? "—"}</strong>
                </article>
              ))}
            </section>
            {error && <p role="alert">{error}</p>}
            <section className="info-card">
              <h2>Choose your workspace</h2>
              <a className="text-link" href="#/guide">First visit? Follow the guided walkthrough →</a>
              <p>
                Run the saved classifier on compatible TIFFs, compare model
                results, or explore the simulated farm grid.
              </p>
              <div className="workspace-cards">
                {(["map", "inference", "models", "data"] as Page[]).map(
                  (key) => (
                    <a key={key} href={`#/${key}`}>
                      <strong>{pages[key][0]} →</strong>
                      <span>{pages[key][1]}</span>
                    </a>
                  ),
                )}
              </div>
              <p>
                Predictions describe Health, Other and Rust image patches. Farm
                scores and timeline stages are simulations; chemical diagnosis
                and forecasting are not established.
              </p>
            </section>
          </>
        )}
        {page === "guide" && <DashboardGuide />}
        {page === "map" && (
          <>
            <p className="notice">
              SIMULATED DATA · Invented farm coordinates and timeline stages. No
              measured farm risk.
            </p>
            <FarmMap />
          </>
        )}
        {page === "inference" && <InferencePanel />}
        {page === "models" && (
          <>
            <WeekThreeResults />
            <ModelResults />
          </>
        )}
        {page === "data" && (
          <>
            {error && <p role="alert">{error}</p>}
            <section className="info-card" id="preparation">
              <span className="eyebrow">DATA PREPARATION</span>
              <h2>From many bands to useful patterns.</h2>
              <p>
                Think of each image as a stack of 125 transparent pages. PCA
                makes 16 new pages that preserve much of the variation.
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

            <SpectralExplorer />
            <MidReview />
          </>
        )}
        <footer>
          TerraSpectra · Crop health analytics
          <span>Data first. Clear assumptions. Measurable progress.</span>
        </footer>
      </main>
    </div>
  );
}
