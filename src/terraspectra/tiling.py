"""Read 64-pixel windows, classify them, and stitch patch scores onto a raster."""
import argparse
import json
import math
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window
import torch

from terraspectra.data import ROOT, make_input
from terraspectra.model import load_model


class TilePredictor:
    """Load once, reuse for many windows. CPU inference keeps setup simple."""

    def __init__(self, model_dir=ROOT / 'models/week3'):
        model_dir = Path(model_dir)
        torch.set_num_threads(2)
        self.model, metadata = load_model(model_dir / 'hybrid_vit.pt')
        self.classes = metadata['class_names']
        with np.load(model_dir / 'preprocessing.npz', allow_pickle=False) as recipe:
            self.recipe = {key: recipe[key].copy() for key in recipe.files}

    def predict_cube(self, cube):
        """One padded 64×64×125 float cube → three uncalibrated scores."""
        if cube.shape != (64, 64, 125) or not np.isfinite(cube).all():
            raise ValueError('Expected a finite 64×64×125 tile.')
        pixels = cube.reshape(-1, 125).astype(np.float32, copy=True)
        pixels -= self.recipe['scaler_mean']
        pixels /= self.recipe['scaler_scale']
        reduced = pixels @ self.recipe['pca_components'].T
        reduced -= self.recipe['pca_mean'] @ self.recipe['pca_components'].T
        inputs = make_input(reduced.reshape(64, 64, 16).astype('float32'))
        with torch.inference_mode():
            return self.model(inputs.unsqueeze(0)).softmax(1)[0].numpy()


def windows(width, height):
    for row in range(0, height, 64):
        for col in range(0, width, 64):
            yield Window(col, row, min(64, width-col), min(64, height-row))


def classify_raster(source, output, predictor=None, max_tiles=4096, patch_only=False):
    """Nonoverlapping windows; edge-repeat padding, then crop writes to real bounds."""
    source, output = Path(source), Path(output)
    if output.exists():
        raise ValueError('Output already exists; choose a new filename.')
    if max_tiles < 1:
        raise ValueError('max_tiles must be positive.')
    if source.resolve() == output.resolve():
        raise ValueError('Input and output must be different files.')
    predictor = predictor or TilePredictor()
    cells = []
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        # Restrict decoding to TIFF; do not accept VRTs referencing other files/URLs.
        with rasterio.Env(GDAL_CACHEMAX=32*1024*1024), rasterio.open(source, driver='GTiff') as src:
            if src.count not in (125, 126):
                raise ValueError('Expected 125 spectral bands, optionally plus one binary extra band.')
            if patch_only and (src.width, src.height) != (64,64):
                raise ValueError('The patch endpoint requires exactly 64×64 pixels. Use the tiling endpoint.')
            count = math.ceil(src.width/64) * math.ceil(src.height/64)
            if count > max_tiles:
                raise ValueError(f'Too many tiles: {count}; limit is {max_tiles}. Use a smaller raster.')
            # Avoid carrying input photometric/interleave/nodata options into a score raster.
            profile = dict(driver='GTiff', width=src.width, height=src.height, count=4,
                           dtype='float32', crs=src.crs, transform=src.transform,
                           tiled=True, blockxsize=64, blockysize=64, compress='deflate')
            with rasterio.open(output, 'w', **profile) as dst:
                for index, name in enumerate([*predictor.classes, 'class_id'], 1):
                    dst.set_band_description(index, name)
                dst.update_tags(meaning='Patch scores repeated over each tile; NOT pixel segmentation',
                                geolocation='Source metadata copied unchanged; NOT independently validated')
                for window in windows(src.width, src.height):
                    raw = src.read(window=window, masked=True).astype('float32')
                    if np.ma.getmaskarray(raw).any() or not np.isfinite(raw.data).all():
                        raise ValueError('Nodata, masked or non-finite pixels found. No imputation is assumed.')
                    if src.count == 126 and not np.isin(raw.data[125], [0,65535]).all():
                        raise ValueError('The extra band must contain only 0 or 65535.')
                    cube = np.moveaxis(raw.data[:125], 0, -1)
                    height, width = cube.shape[:2]
                    padded = np.pad(cube, ((0,64-height),(0,64-width),(0,0)), mode='edge')
                    scores = predictor.predict_cube(padded)
                    class_id = int(scores.argmax())
                    values = np.r_[scores, np.float32(class_id)].astype('float32')
                    stitched = np.broadcast_to(values[:,None,None], (4,height,width)).copy()
                    dst.write(stitched, window=window)
                    cells.append({'row': int(window.row_off), 'column': int(window.col_off),
                                  'height': height, 'width': width, 'edge_padded': height < 64 or width < 64,
                                  'class_id': class_id, 'predicted_class': predictor.classes[class_id],
                                  'scores': dict(zip(predictor.classes, map(float,scores)))})
            return {'schema_version': 1, 'model': 'Week 3 CNN + vision transformer',
                    'width': src.width, 'height': src.height, 'tiles': cells, 'tile_count': len(cells),
                    'source_crs': str(src.crs) if src.crs else None, 'source_transform': list(src.transform)[:6],
                    'band_order': [*predictor.classes, 'class_id'],
                    'note': 'Tile-level classification, not pixel segmentation. Scores uncalibrated. '
                            'Matching band count alone does not establish sensor compatibility. '
                            'Source georeferencing is copied, not validated. Edge padding is experimental.'}
    except Exception:
        output.unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--max-tiles', type=int, default=4096)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output already exists; choose a new filename.')
    report = classify_raster(args.source, args.output, max_tiles=args.max_tiles)
    args.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"Wrote {report['tile_count']} tile predictions to {args.output}")


if __name__ == '__main__':
    main()
