import { useEffect, useState } from "react";

type Audit = {
  extraction: { files_checked: number; integrity_passed: boolean };
  gis: {
    cells_checked: number;
    grid_alignment_passed: boolean;
    max_corner_error_degrees: number;
    real_farm_alignment: string;
    browser_camera_alignment: string;
  };
  memory_trials: {
    batch_size: number;
    peak_process_rss_mib: number;
    input_mib: number;
    seconds: number;
  }[];
};

export default function MidReview() {
  const [audit, setAudit] = useState<Audit | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    fetch("/mid-review.json")
      .then((response) => {
        if (!response.ok) throw new Error("Data quality report unavailable.");
        return response.json();
      })
      .then(setAudit)
      .catch((error) => setError(String(error)));
  }, []);
  return (
    <section className="info-card" id="data-quality">
      <h2>Data quality & map alignment</h2>
      <p>
        Dataset integrity, memory measurements, and demonstration grid
        alignment.
      </p>
      {error && <p role="alert">{error}</p>}
      {!audit && !error && <p>Loading audit results…</p>}
      {audit && (
        <>
          <p>
            <strong>{audit.extraction.files_checked} files checked</strong> ·
            ZIP, extracted files, and manifest hashes{" "}
            {audit.extraction.integrity_passed ? "match" : "do not match"}.
          </p>
          <h3>CPU memory measurements</h3>
          <p>
            Each batch ran three training steps in a fresh process. Peak memory
            includes Python, libraries, cached data, and model work.
          </p>
          <div style={{ overflowX: "auto" }}>
            <table>
              <thead>
                <tr>
                  <th>Batch</th>
                  <th>Input MiB</th>
                  <th>Peak process MiB</th>
                  <th>Seconds</th>
                </tr>
              </thead>
              <tbody>
                {audit.memory_trials.map((trial) => (
                  <tr key={trial.batch_size}>
                    <td>{trial.batch_size}</td>
                    <td>{trial.input_mib.toFixed(3)}</td>
                    <td>{trial.peak_process_rss_mib.toFixed(1)}</td>
                    <td>{trial.seconds.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <h3>Map coordinate checks</h3>
          <p>
            {audit.gis.cells_checked} synthetic cells:{" "}
            {audit.gis.grid_alignment_passed
              ? "coordinate checks passed"
              : "check failed"}
            . Maximum corner error:{" "}
            {audit.gis.max_corner_error_degrees.toExponential(2)}°.
          </p>
          <p>{audit.gis.real_farm_alignment}</p>
          <p>{audit.gis.browser_camera_alignment}</p>
          <p>
            This validates the demonstration grid’s geometry. The dataset cannot
            locate disease on this farm.
          </p>
        </>
      )}
    </section>
  );
}
