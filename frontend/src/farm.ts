import type { FeatureCollection, Polygon } from "geojson";
import boundary from "./demo-farm.json";

// The audit reads this same synthetic boundary. It does not locate Kaggle images.
export const FARM_CENTER: [number, number] = [77.595, 13.155];
export const demoFarm = boundary as FeatureCollection<Polygon>;
