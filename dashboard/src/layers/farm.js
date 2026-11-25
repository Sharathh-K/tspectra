import { BitmapLayer, PathLayer, PolygonLayer } from '@deck.gl/layers';

export function farmLayers(scene, grid, layers, selected, onSelect) {
  const [nw, ne, se, sw] = grid.boundary;
  return [
    new BitmapLayer({ id: 'spectral-image', image: scene.image, bounds: [sw, nw, ne, se],
      visible: layers.image }),
    new PolygonLayer({ id: 'stress-cells', data: grid.cells, getPolygon: d => d.polygon,
      getFillColor: d => layers.stress ? (d.label ? [255, 122, 62, 245] : [49, 130, 98, 105]) : [0, 0, 0, 1],
      updateTriggers: { getFillColor: [layers.stress], getElevation: [layers.stress] },
      extruded: layers.stress, getElevation: d => layers.stress && d.label ? 16 : 0,
      stroked: false, pickable: true, onClick: info => onSelect(info.object ?? null) }),
    new PathLayer({ id: 'field-boundary', visible: layers.boundary, data: [[...grid.boundary, nw]],
      getPath: d => d, getColor: [212, 244, 169], getWidth: 2, widthUnits: 'pixels' }),
    new PathLayer({ id: 'selection', data: selected ? [selected] : [],
      getPath: d => [...d.polygon, d.polygon[0]].map(([x,y]) => [x,y,18]),
      getColor: [255,255,255], getWidth: 3, widthUnits: 'pixels' })
  ];
}
