import { useEffect, useMemo, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import { MapboxOverlay } from "@deck.gl/mapbox";
import { GeoJsonLayer } from "@deck.gl/layers";
import { demoFarm, FARM_CENTER } from "./farm";
import {
  Cell,
  MockHeatmap,
  cellFeatures,
  parseHeatmap,
  scoreColor,
} from "./heatmap";
import AnalyticsPanel from "./AnalyticsPanel";
import HeatmapPreview from "./HeatmapPreview";

export default function FarmMap() {
  const container = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const overlay = useRef<MapboxOverlay | null>(null);
  const [showBoundary, setShowBoundary] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [opacity, setOpacity] = useState(0.75);
  const [threshold, setThreshold] = useState(0);
  const [selected, setSelected] = useState<Cell | null>(null);
  const [sourceData, setData] = useState<MockHeatmap | null>(null);
  const [frame, setFrame] = useState(2);
  // Invented stages, not dated observations or forecasts.
  const data = useMemo(
    () =>
      sourceData
        ? {
            ...sourceData,
            cells: sourceData.cells.map((cell) => ({
              ...cell,
              score: Math.min(1, cell.score * [0.6, 0.8, 1, 1.15][frame]),
            })),
          }
        : null,
    [sourceData, frame],
  );
  useEffect(() => setSelected(null), [frame]);
  const [dataError, setDataError] = useState("");
  const [mapFailed, setMapFailed] = useState(false);
  const [status, setStatus] = useState("Loading satellite map…");
  const token = import.meta.env.VITE_MAPBOX_TOKEN;
  const hasToken = Boolean(token && !token.includes("your_public_token"));

  useEffect(() => {
    const controller = new AbortController();
    fetch("/mock-heatmap.json", { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error("Could not load mock heatmap.");
        return response.json();
      })
      .then((value) => setData(parseHeatmap(value)))
      .catch((error) => {
        if (error.name !== "AbortError")
          setDataError("Heatmap data could not be loaded or validated.");
      });
    return () => controller.abort();
  }, []);

  const visibleCells = useMemo(
    () => data?.cells.filter((cell) => cell.score >= threshold) ?? [],
    [data, threshold],
  );
  useEffect(() => {
    if (!showHeatmap || (selected && selected.score < threshold))
      setSelected(null);
  }, [threshold, showHeatmap, selected]);

  // Both views use the same coordinates and colour rules.
  const layers = useMemo(
    () => [
      new GeoJsonLayer<Cell>({
        id: "mock-heatmap",
        data: cellFeatures(visibleCells),
        visible: showHeatmap,
        filled: true,
        stroked: true,
        opacity,
        pickable: true,
        getFillColor: (feature) => scoreColor(feature.properties.score),
        getLineColor: (feature) =>
          feature.properties.id === selected?.id
            ? [255, 255, 255, 255]
            : [30, 50, 35, 100],
        getLineWidth: (feature) =>
          feature.properties.id === selected?.id ? 3 : 1,
        lineWidthUnits: "pixels",
        onClick: (info) => setSelected(info.object?.properties ?? null),
        updateTriggers: {
          getLineColor: selected?.id,
          getLineWidth: selected?.id,
        },
      }),
      new GeoJsonLayer({
        id: "demo-farm-boundary",
        data: demoFarm,
        visible: showBoundary,
        filled: false,
        stroked: true,
        getLineColor: [199, 238, 158, 255],
        getLineWidth: 3,
        lineWidthUnits: "pixels",
        pickable: false,
      }),
    ],
    [visibleCells, showHeatmap, opacity, selected, showBoundary],
  );
  const currentLayers = useRef(layers);
  currentLayers.current = layers;

  useEffect(() => {
    if (!hasToken || !container.current) return;
    let instance: mapboxgl.Map | undefined;
    try {
      instance = new mapboxgl.Map({
        container: container.current,
        accessToken: token,
        style: "mapbox://styles/mapbox/satellite-streets-v12",
        center: FARM_CENTER,
        zoom: 14,
        pitch: 45,
        bearing: -15,
      });
      map.current = instance;
      instance.addControl(new mapboxgl.NavigationControl(), "top-right");
      const deck = new MapboxOverlay({
        interleaved: false,
        layers: currentLayers.current,
      });
      overlay.current = deck;
      instance.addControl(deck);
      instance.on("load", () =>
        setStatus("Satellite map with simulated heatmap"),
      );
      instance.on("error", () => {
        setStatus("Map unavailable. Check your public token and connection.");
        setMapFailed(true);
      });
    } catch {
      setStatus("Map unavailable. Diagram preview remains interactive.");
      setMapFailed(true);
    }
    return () => {
      instance?.remove();
      map.current = null;
      overlay.current = null;
    };
  }, [hasToken, token]);

  useEffect(() => {
    overlay.current?.setProps({ layers });
  }, [layers]);

  return (
    <section
      className="heatmap-workspace"
      aria-label="Simulated heatmap workspace"
    >
      <div className="heatmap-controls">
        <label>
          Simulated timeline · stage {frame + 1} of 4
          <input
            aria-label="Simulated timeline stage"
            type="range"
            min="0"
            max="3"
            step="1"
            value={frame}
            onChange={(event) => setFrame(Number(event.target.value))}
          />
        </label>
        <span>Invented progression · no observation dates or forecasts</span>
        <label>
          <input
            type="checkbox"
            checked={showHeatmap}
            onChange={(event) => setShowHeatmap(event.target.checked)}
          />{" "}
          Show heatmap
        </label>
        <label>
          <input
            type="checkbox"
            checked={showBoundary}
            onChange={(event) => setShowBoundary(event.target.checked)}
          />{" "}
          Farm boundary
        </label>
        <label>
          Opacity{" "}
          <input
            aria-label="Heatmap opacity"
            type="range"
            min="0.1"
            max="1"
            step="0.05"
            value={opacity}
            onChange={(event) => setOpacity(Number(event.target.value))}
          />
          <output>{Math.round(opacity * 100)}%</output>
        </label>
        <label>
          Minimum score{" "}
          <input
            aria-label="Minimum simulated score"
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={threshold}
            onChange={(event) => setThreshold(Number(event.target.value))}
          />
          <output>{threshold.toFixed(2)}</output>
        </label>
      </div>
      <div className="map-panel">
        <div ref={container} className="map-canvas" />
        {(!hasToken || mapFailed) && (
          <div className="map-placeholder">
            <div className="coordinate-grid" />
            {data && !dataError && (
              <HeatmapPreview
                data={data}
                visible={showHeatmap}
                boundary={showBoundary}
                threshold={threshold}
                opacity={opacity}
                selected={selected?.id ?? null}
                onSelect={setSelected}
              />
            )}
          </div>
        )}
        {dataError && (
          <div className="heatmap-message" role="alert">
            {dataError}
          </div>
        )}
        {!data && !dataError && (
          <div className="heatmap-message" role="status">
            Loading simulated cells…
          </div>
        )}
        <div className="map-top">
          <span className="map-tag">
            {hasToken && !mapFailed
              ? "SATELLITE + SIMULATION"
              : "INTERACTIVE DIAGRAM"}
          </span>
          <button
            disabled={!hasToken || mapFailed}
            onClick={() =>
              map.current?.flyTo({
                center: FARM_CENTER,
                zoom: 14,
                pitch: 45,
                bearing: -15,
              })
            }
          >
            Reset view ↗
          </button>
        </div>
        <div className="map-bottom">
          <span>
            SIMULATED DATA · {showHeatmap ? visibleCells.length : 0}/
            {data?.cells.length ?? 0} cells shown
          </span>
          <span>
            {hasToken ? status : "Add a Mapbox public token for satellite view"}
          </span>
        </div>
      </div>
      {data && <AnalyticsPanel data={data} threshold={threshold} />}
      <div className="heatmap-details">
        <div className="heatmap-legend" aria-label="Simulated score legend">
          <b>SIMULATED SCORE</b>
          <span>
            <i style={{ background: "#64c08a" }} />
            0–&lt;0.33
          </span>
          <span>
            <i style={{ background: "#edbb53" }} />
            0.33–&lt;0.66
          </span>
          <span>
            <i style={{ background: "#e16655" }} />
            0.66–1
          </span>
        </div>
        <p aria-live="polite">
          {selected
            ? `${selected.id} · Score ${selected.score.toFixed(3)} · Invented, not a model prediction`
            : "Select a cell to inspect its simulated score."}
        </p>
      </div>
    </section>
  );
}
