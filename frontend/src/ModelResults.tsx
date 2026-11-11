import { useEffect, useState } from "react";

type Scores = {
  accuracy: number;
  macro_f1: number;
  confusion_matrix: number[][];
};
type Report = {
  model: string;
  parameters: number;
  best_epoch: number;
  epochs_run: number;
  elapsed_seconds: number;
  peak_process_memory_mib: number;
  device: string;
  cnn: Scores;
  baseline: Scores;
  classes: string[];
};

export default function ModelResults() {
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    fetch("/model-summary.json", { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error();
        return response.json();
      })
      .then(setReport)
      .catch((error) => {
        if (error.name !== "AbortError")
          setError("Classifier performance report unavailable.");
      });
    return () => controller.abort();
  }, []);
  return (
    <section className="info-card model-results" id="model-results">
      <span className="eyebrow">
        REAL TRAINING RESULTS / DEVELOPMENT VALIDATION
      </span>
      <h2>A small model, measured honestly.</h2>
      <p>
        Results below use the 120 labelled validation patches. The map above
        uses independent simulated data.
      </p>
      {error && <p role="alert">{error}</p>}
      {!report && !error && <p>Loading the training report…</p>}
      {report && (
        <>
          <div className="model-comparison">
            <table>
              <caption>Same development split for both models</caption>
              <thead>
                <tr>
                  <th scope="col">Model</th>
                  <th scope="col">Accuracy</th>
                  <th scope="col">Macro F1</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["Hybrid 3D–2D CNN", report.cnn],
                  ["Logistic baseline", report.baseline],
                ].map(([name, scores]) => {
                  const result = scores as Scores;
                  return (
                    <tr key={String(name)}>
                      <th scope="row">{String(name)}</th>
                      <td>{(result.accuracy * 100).toFixed(1)}%</td>
                      <td>{result.macro_f1.toFixed(3)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            <div className="training-facts">
              <span>
                <b>{report.parameters.toLocaleString()}</b> model parameters
              </span>
              <span>
                <b>{report.elapsed_seconds.toFixed(1)} seconds</b> measured
                local run · {report.device.toUpperCase()}
              </span>
              <span>
                <b>Epoch {report.best_epoch}</b> saved from {report.epochs_run}{" "}
                epochs
              </span>
            </div>
          </div>
          <p>
            {report.baseline.macro_f1 > report.cnn.macro_f1
              ? "The baseline has the higher macro F1. The CNN is not better on every measure."
              : "Compare accuracy and macro F1 before choosing a model."}
          </p>
          <p className="evaluation-note">
            Checkpoint selection used this validation set. These are development
            scores, not an independent test or evidence of performance on new
            farms. Runtime varies by machine.
          </p>
        </>
      )}
    </section>
  );
}
