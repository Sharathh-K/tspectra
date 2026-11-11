import type { MockHeatmap } from "./heatmap";

// Area of a longitude/latitude rectangle on a sphere, not a surveyed area.
export function acres(bounds: number[]) {
  const [west, south, east, north] = bounds;
  const radians = Math.PI / 180;
  return (
    (6371008.8 ** 2 *
      (east - west) *
      radians *
      (Math.sin(north * radians) - Math.sin(south * radians))) /
    4046.8564224
  );
}

export default function AnalyticsPanel({
  data,
  threshold,
}: {
  data: MockHeatmap;
  threshold: number;
}) {
  const total = data.cells.reduce((sum, cell) => sum + acres(cell.bounds), 0);
  const selected = data.cells.filter((cell) => cell.score >= threshold);
  const flagged = selected.reduce((sum, cell) => sum + acres(cell.bounds), 0);
  const bins = [
    {
      name: "Low (0–<0.33)",
      color: "#64c08a",
      cells: data.cells.filter((c) => c.score < 0.33),
    },
    {
      name: "Medium (0.33–<0.66)",
      color: "#edbb53",
      cells: data.cells.filter((c) => c.score >= 0.33 && c.score < 0.66),
    },
    {
      name: "High (0.66–1)",
      color: "#e16655",
      cells: data.cells.filter((c) => c.score >= 0.66),
    },
  ];
  return (
    <aside
      className="info-card analytics-panel"
      id="analytics"
      aria-label="Simulation analytics"
    >
      <span className="eyebrow">WEEK 3 / SIMULATION ANALYTICS</span>
      <h2>How much demonstration area is flagged?</h2>
      <p>
        <strong>{flagged.toFixed(1)} acres</strong> of {total.toFixed(1)}{" "}
        simulated acres at score ≥ {threshold.toFixed(2)} ({selected.length}{" "}
        cells).
      </p>
      <p>
        Move the map’s minimum-score slider to change this estimate. Hiding the
        layer does not change the selected data.
      </p>
      <h3>Whole-grid score distribution</h3>
      {bins.map((bin) => (
        <div key={bin.name} style={{ marginBottom: "12px" }}>
          <label>
            {bin.name}: {bin.cells.length} cells ·{" "}
            {bin.cells.reduce((s, c) => s + acres(c.bounds), 0).toFixed(1)}{" "}
            acres
          </label>
          <div
            style={{
              background: "#23342d",
              height: "12px",
              borderRadius: "6px",
            }}
          >
            <div
              style={{
                width: `${(100 * bin.cells.length) / data.cells.length}%`,
                background: bin.color,
                height: "100%",
                borderRadius: "6px",
              }}
            />
          </div>
        </div>
      ))}
      <p>
        Approximate spherical area of an invented boundary. These scores are not
        model predictions, infection probabilities, or measured crop damage.
      </p>
      <h3>Chemical anomalies: unavailable</h3>
      <p>
        The dataset provides Health, Other and Rust patch labels. It has no
        verified chemical concentrations or deficiency labels. “Other” is not a
        chemical diagnosis.
      </p>
    </aside>
  );
}
