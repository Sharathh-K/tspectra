import { useEffect, useState } from "react";
type Scores = {
  accuracy: number;
  macro_f1: number;
  per_class: Record<string, { recall: number }>;
};
type Report = {
  transformer: Scores;
  baseline: Scores;
  elapsed_seconds: number;
  parameters: number;
  best_epoch: number;
  classes: string[];
};
export default function WeekThreeResults() {
  const [results, setResults] = useState<{
    current: Report;
    previous: { cnn: Scores };
  } | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    Promise.all(
      ["/week3-summary.json", "/model-summary.json"].map(async (url) => {
        const response = await fetch(url, { signal: controller.signal });
        if (!response.ok) throw new Error("Model comparison unavailable.");
        return response.json();
      }),
    )
      .then(([current, previous]) => setResults({ current, previous }))
      .catch((error) => {
        if (error.name !== "AbortError") setError(String(error));
      });
    return () => controller.abort();
  }, []);
  return (
    <section className="info-card model-results" id="week-three">
      <span className="eyebrow">WEEK 3 / REAL PATCH CLASSIFICATION</span>
      <h2>Did self-attention help?</h2>
      {error && <p role="alert">{error}</p>}
      {!results && !error && <p>Loading comparison…</p>}
      {results && (
        <>
          <div className="model-comparison">
            <table>
              <caption>Same 120 development-validation patches</caption>
              <thead>
                <tr>
                  <th>Model</th>
                  <th>Accuracy</th>
                  <th>Macro F1</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["Week 3 CNN + transformer", results.current.transformer],
                  ["Week 2 CNN", results.previous.cnn],
                  ["Logistic baseline", results.current.baseline],
                ].map(([name, score]) => {
                  const metric = score as Scores;
                  return (
                    <tr key={String(name)}>
                      <th>{String(name)}</th>
                      <td>{(100 * metric.accuracy).toFixed(1)}%</td>
                      <td>{metric.macro_f1.toFixed(3)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p>
            {results.current.parameters.toLocaleString()} parameters ·{" "}
            {results.current.elapsed_seconds.toFixed(1)} seconds on CPU · saved
            epoch {results.current.best_epoch}.
          </p>
          <h3>Recall: how many actual examples were found?</h3>
          {results.current.classes.map((name) => (
            <p key={name}>
              {name}:{" "}
              {(
                results.current.transformer.per_class[name].recall * 100
              ).toFixed(1)}
              %
            </p>
          ))}
          <p>
            Macro F1 change versus Week 2:{" "}
            {(
              results.current.transformer.macro_f1 -
              results.previous.cnn.macro_f1
            ).toFixed(3)}
            . Higher is better; this single run does not isolate attention’s
            effect from other architecture changes.
          </p>
          <p>
            These scores selected the checkpoint, so they are not an independent
            test. No chemical diagnosis or real-farm forecast is established.
          </p>
        </>
      )}
    </section>
  );
}
