import type { FeatureCollection, Polygon } from "geojson";

// Invented boundary near Bengaluru. It does not locate the Kaggle images.
export const FARM_CENTER: [number, number] = [77.595, 13.155];
export const demoFarm: FeatureCollection<Polygon> = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: { name: "Demonstration farm", source: "Synthetic boundary" },
      geometry: {
        type: "Polygon",
        // GeoJSON uses longitude first, latitude second. Close the ring.
        coordinates: [
          [
            [77.591, 13.152],
            [77.599, 13.152],
            [77.599, 13.158],
            [77.591, 13.158],
            [77.591, 13.152],
          ],
        ],
      },
    },
  ],
};
