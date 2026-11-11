import { useEffect, useRef, useState } from "react";

type Prediction = {
  tile_count: number;
  note: string;
  tiles: { predicted_class: string; scores: Record<string, number> }[];
};
export default function InferencePanel() {
  const [service, setService] = useState("Service status not checked.");
  const [checking, setChecking] = useState(false);
  async function checkService() {
    setChecking(true);
    try {
      const response = await fetch("/api/health", {signal: AbortSignal.timeout(5000)});
      if (!response.ok) throw new Error();
      const data = await response.json();
      if (data.status !== "ready") throw new Error();
      setService(data.busy ? "Service is busy. Retry shortly." : "Service ready · CPU · saved CNN + Transformer");
    } catch { setService("Service unavailable. Start the local API on port 8000, then retry."); }
    finally { setChecking(false); }
  }
  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState("predict");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("");
  const [result, setResult] = useState<Prediction | null>(null);
  const [download, setDownload] = useState("");
  const abort = useRef<AbortController | null>(null);
  useEffect(() => () => abort.current?.abort(), []);
  useEffect(
    () => () => {
      if (download) URL.revokeObjectURL(download);
    },
    [download],
  );
  async function submit() {
    if (!file) {
      setStatus("Choose a TIFF first.");
      return;
    }
    if (file.size > 128 * 1024 * 1024) {
      setStatus("Choose a file smaller than 128 MiB.");
      return;
    }
    setBusy(true);
    setResult(null);
    setDownload("");
    setStatus("Uploading and processing locally…");
    const controller = new AbortController();
    abort.current = controller;
    try {
      const response = await fetch(`/api/${mode}`, {
        method: "POST",
        headers: { "Content-Type": "application/octet-stream" },
        body: file,
        signal: controller.signal,
      });
      if (!response.ok) {
        const error = await response.json().catch(() => null);
        throw new Error(
          error?.detail ??
            `Service returned ${response.status}. Start the local API on port 8000.`,
        );
      }
      if (mode === "tile") {
        setDownload(URL.createObjectURL(await response.blob()));
        setStatus(
          "Tiled prediction ready. Download the score raster and JSON summary.",
        );
      } else {
        setResult(await response.json());
        setStatus("Patch classification complete.");
      }
    } catch (error) {
      setStatus(
        error instanceof Error
          ? error.name === "AbortError"
            ? "Request cancelled. Server work may finish before cleanup."
            : error.message
          : "Start the local API on port 8000 and retry.",
      );
    } finally {
      setBusy(false);
      abort.current = null;
    }
  }
  return (
    <section className="info-card" id="inference">
      <span className="eyebrow">LOCAL MODEL SERVICE</span>
      <h2>Predict a patch or tile a compatible TIFF</h2>
      <p>
        Use the supplied dataset’s band order and scale. RGB photos and
        arbitrary satellite images are not compatible. Maximum upload: 128 MiB /
        256 tiles.
      </p>
      <p role="status">{service}</p>
      <button disabled={checking} onClick={checkService}>{checking ? "Checking…" : "Check service"}</button>
      <details className="usage-help"><summary>Which input should I choose?</summary><p>Example: use an original 64 × 64 TIFF from train/Health for patch mode. Its folder label is a reference answer; the model can still predict another class. Tiled mode accepts a larger raster only when its spectral bands and sensor scale match the training data. The ZIP contains predictions.tif and summary.json.</p></details>
      <div className="heatmap-controls">
        <label>
          TIFF{" "}
          <input
            disabled={busy}
            type="file"
            accept=".tif,.tiff"
            onChange={(e) => {
              setFile(e.target.files?.[0] ?? null);
              setResult(null);
              setDownload("");
              setStatus("");
            }}
          />
        </label>
        <label>
          Mode{" "}
          <select
            disabled={busy}
            value={mode}
            onChange={(e) => {
              setMode(e.target.value);
              setResult(null);
              setDownload("");
              setStatus("");
            }}
          >
            <option value="predict">One 64×64 patch → JSON</option>
            <option value="tile">Tiled raster → ZIP download</option>
          </select>
        </label>
        <button disabled={busy || !file} onClick={submit}>
          {busy ? "Processing…" : "Run inference"}
        </button>
        {busy && (
          <button onClick={() => abort.current?.abort()}>Cancel request</button>
        )}
      </div>
      <p role="status" aria-live="polite">
        {status}
      </p>
      {download && (
        <a href={download} download="terraspectra-predictions.zip">
          Download prediction TIFF + summary ZIP
        </a>
      )}
      {result && (
        <>
          <h3>Predicted patch class: {result.tiles[0].predicted_class}</h3>
          {Object.entries(result.tiles[0].scores).map(([name, score]) => (
            <p key={name}>
              {name}: {(score * 100).toFixed(1)}% uncalibrated score
            </p>
          ))}
          <p>{result.note}</p>
        </>
      )}
      <p>
        The output repeats one class-score vector over each tile. It is not a
        pixel disease mask. Upload predictions do not replace the independent
        simulated farm map.
      </p>
    </section>
  );
}
