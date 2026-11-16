import { useMemo } from "react";
import DeckGL from "@deck.gl/react";
import { GeoJsonLayer } from "@deck.gl/layers";
import Map from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

import { INITIAL_VIEW_STATE, MAP_STYLE } from "../config";
import { farmBoundary } from "../data/farm";

export default function MapView() {
  const layers = useMemo(
    () => [
      new GeoJsonLayer({
        id: "farm-boundary",
        data: farmBoundary,
        stroked: true,
        filled: true,
        getFillColor: [34, 139, 34, 60],
        getLineColor: [0, 100, 0, 255],
        getLineWidth: 1,
        lineWidthMinPixels: 2,
      }),
    ],
    []
  );

  return (
    <DeckGL
      initialViewState={INITIAL_VIEW_STATE}
      controller={true}
      layers={layers}
    >
      <Map mapStyle={MAP_STYLE} />
    </DeckGL>
  );
}
