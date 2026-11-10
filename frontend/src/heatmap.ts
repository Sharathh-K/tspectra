import type { FeatureCollection, Polygon } from "geojson";

export type Cell = {
  id: string;
  row: number;
  column: number;
  bounds: [number, number, number, number];
  score: number;
};
export type MockHeatmap = {
  schema_version: number;
  is_mock: true;
  source: string;
  score_meaning: string;
  crs: string;
  bounds: number[];
  rows: number;
  columns: number;
  cells: Cell[];
};

export function parseHeatmap(value: unknown): MockHeatmap {
  const data = value as MockHeatmap;
  if (
    !data ||
    data.is_mock !== true ||
    data.schema_version !== 1 ||
    data.crs !== "EPSG:4326" ||
    !Number.isInteger(data.rows) ||
    !Number.isInteger(data.columns) ||
    data.rows < 1 ||
    data.columns < 1 ||
    data.rows * data.columns > 10000 ||
    !Array.isArray(data.bounds) ||
    data.bounds.length !== 4 ||
    !data.bounds.every(Number.isFinite) ||
    !Array.isArray(data.cells) ||
    data.cells.length !== data.rows * data.columns
  ) {
    throw new Error("Invalid mock heatmap response.");
  }
  const [west, south, east, north] = data.bounds;
  if (
    west >= east ||
    south >= north ||
    west < -180 ||
    east > 180 ||
    south < -90 ||
    north > 90
  ) {
    throw new Error("Invalid geographic bounds.");
  }
  const ids = new Set<string>();
  const positions = new Set<string>();
  for (const cell of data.cells) {
    if (
      typeof cell.id !== "string" ||
      ids.has(cell.id) ||
      !Number.isInteger(cell.row) ||
      !Number.isInteger(cell.column) ||
      cell.row < 0 ||
      cell.row >= data.rows ||
      cell.column < 0 ||
      cell.column >= data.columns ||
      !Number.isFinite(cell.score) ||
      cell.score < 0 ||
      cell.score > 1 ||
      !Array.isArray(cell.bounds) ||
      cell.bounds.length !== 4 ||
      !cell.bounds.every(Number.isFinite)
    ) {
      throw new Error("Invalid cell in mock heatmap.");
    }
    const position = `${cell.row}-${cell.column}`;
    if (positions.has(position)) throw new Error("Duplicate grid position.");
    const expected = [
      west + (cell.column * (east - west)) / data.columns,
      south + (cell.row * (north - south)) / data.rows,
      west + ((cell.column + 1) * (east - west)) / data.columns,
      south + ((cell.row + 1) * (north - south)) / data.rows,
    ];
    if (cell.bounds.some((value, i) => Math.abs(value - expected[i]) > 1e-8)) {
      throw new Error("Cell bounds do not align with the grid.");
    }
    ids.add(cell.id);
    positions.add(position);
  }
  return data;
}

// Fixed bins: zooming the map must not change the meaning of the colours.
export function scoreColor(score: number): [number, number, number, number] {
  if (score < 0.33) return [100, 192, 138, 255];
  if (score < 0.66) return [237, 187, 83, 255];
  return [225, 102, 85, 255];
}

export function cellFeatures(cells: Cell[]): FeatureCollection<Polygon, Cell> {
  return {
    type: "FeatureCollection",
    features: cells.map((cell) => {
      const [west, south, east, north] = cell.bounds;
      return {
        type: "Feature",
        properties: cell,
        geometry: {
          type: "Polygon",
          coordinates: [
            [
              [west, south],
              [east, south],
              [east, north],
              [west, north],
              [west, south],
            ],
          ],
        },
      };
    }),
  };
}
