import { Cell, MockHeatmap, scoreColor } from "./heatmap";

type Props = {
  data: MockHeatmap;
  visible: boolean;
  boundary: boolean;
  threshold: number;
  opacity: number;
  selected: string | null;
  onSelect: (cell: Cell) => void;
};

// A simple interactive diagram works even without a Mapbox token or WebGL.
export default function HeatmapPreview({
  data,
  visible,
  boundary,
  threshold,
  opacity,
  selected,
  onSelect,
}: Props) {
  return (
    <div className="heatmap-preview">
      <span className="preview-north">N ↑</span>
      <svg
        viewBox={`-1 -1 ${data.columns + 2} ${data.rows + 2}`}
        preserveAspectRatio="xMidYMid meet"
        aria-label="Synthetic heatmap diagram"
        role="group"
      >
        <title>Synthetic heatmap diagram, north at the top</title>
        <rect width={data.columns} height={data.rows} fill="#1b3027" />
        {visible &&
          data.cells
            .filter((cell) => cell.score >= threshold)
            .map((cell) => {
              const [r, g, b] = scoreColor(cell.score);
              return (
                <rect
                  key={cell.id}
                  x={cell.column}
                  y={data.rows - 1 - cell.row}
                  width="1"
                  height="1"
                  fill={`rgb(${r},${g},${b})`}
                  fillOpacity={opacity}
                  stroke={selected === cell.id ? "#fff" : "#203b2d"}
                  strokeWidth={selected === cell.id ? 0.09 : 0.025}
                  role="button"
                  tabIndex={0}
                  aria-label={`${cell.id}, simulated score ${cell.score.toFixed(2)}`}
                  onClick={() => onSelect(cell)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      onSelect(cell);
                    }
                  }}
                >
                  <title>
                    {cell.id}: simulated score {cell.score.toFixed(2)}
                  </title>
                </rect>
              );
            })}
        {boundary && (
          <rect
            width={data.columns}
            height={data.rows}
            fill="none"
            stroke="#c7ee9e"
            strokeWidth="0.05"
            pointerEvents="none"
          />
        )}
      </svg>
      <p>Diagram preview · Synthetic cells · No satellite imagery</p>
    </div>
  );
}
