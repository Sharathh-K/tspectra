"""Create a small, explicitly artificial mosaic and demonstrate tiled prediction."""
import json
import tempfile
import time
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from rasterio.windows import Window

from terraspectra.data import ROOT, read_inventory
from terraspectra.tiling import TilePredictor, classify_raster


def make_mosaic(path):
    """Six real training patches arranged artificially; edges deliberately partial."""
    rows = read_inventory()
    examples = [next(r for r in rows if r['split']=='train' and r['label']==label)
                for label in ['Health','Other','Rust']]
    # Synthetic coordinates are for exercising metadata preservation only.
    profile = dict(driver='GTiff',width=130,height=97,count=125,dtype='uint16',
                   crs='EPSG:4326', transform=from_bounds(77.591,13.152,77.599,13.158,130,97),
                   tiled=True,blockxsize=64,blockysize=64,compress='deflate')
    with rasterio.open(path,'w',**profile) as output:
        output.update_tags(source='Artificial arrangement of dataset patches; not a real farm scene')
        for row in range(2):
            for col in range(3):
                with rasterio.open(ROOT/'data/raw'/examples[(row+col)%3]['path']) as image:
                    cube = image.read(list(range(1,126)))
                width,height = min(64,130-col*64),min(64,97-row*64)
                output.write(cube[:,:height,:width],window=Window(col*64,row*64,width,height))


def main():
    directory = ROOT/'reports/week4'
    directory.mkdir(exist_ok=True,parents=True)
    with tempfile.TemporaryDirectory(prefix='terraspectra-demo-') as tmp:
        source, output = Path(tmp)/'artificial.tif', Path(tmp)/'scores.tif'
        make_mosaic(source)
        start = time.perf_counter()
        report = classify_raster(source,output,TilePredictor())
        report['elapsed_seconds_including_model_load'] = time.perf_counter()-start
        report['demonstration'] = 'Artificial 130×97 mosaic; not a real satellite or temporal scene'
        with rasterio.open(output) as image:
            classes, rust = image.read(4), image.read(3)
            report['output_shape_bhw'] = [image.count,image.height,image.width]
        fig, axes = plt.subplots(1,2,figsize=(10,4))
        a = axes[0].imshow(classes,vmin=0,vmax=2,cmap='viridis',interpolation='nearest')
        fig.colorbar(a,ax=axes[0],ticks=[0,1,2],label='0 Health / 1 Other / 2 Rust')
        axes[0].set_title('Patch class repeated over each tile')
        b = axes[1].imshow(rust,vmin=0,vmax=1,cmap='magma',interpolation='nearest')
        fig.colorbar(b,ax=axes[1],label='Uncalibrated Rust score')
        axes[1].set_title('Artificial mosaic — not pixel diagnosis')
        for ax in axes:
            ax.set(xlabel='Pixel column',ylabel='Pixel row')
        fig.tight_layout(); fig.savefig(directory/'tiling_demo.png',dpi=140); plt.close(fig)
        (directory/'tiling_demo.json').write_text(json.dumps(report,indent=2)+'\n')
        print(f"Demonstrated {report['tile_count']} tiles; output {report['output_shape_bhw']}")


if __name__ == '__main__':
    main()
