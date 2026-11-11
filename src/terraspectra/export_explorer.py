"""Export six small, reproducible previews; never copy raw cubes into the website."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

import numpy as np
from rasterio.io import MemoryFile
import matplotlib
matplotlib.use('Agg')
from matplotlib import image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', required=True, type=Path)
    parser.add_argument('--output', type=Path, default=Path('frontend/public/explorer'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    samples = []
    with zipfile.ZipFile(args.zip) as archive:
        for label in ['Health', 'Other', 'Rust']:
            names = sorted(n for n in archive.namelist()
                           if n.startswith(f'train/{label}/') and n.endswith('.tif'))[:2]
            for index, name in enumerate(names):
                raw = archive.read(name)
                with MemoryFile(raw) as memory:
                    with memory.open() as dataset:
                        cube = dataset.read(list(range(1, 126))).astype(np.float32)
                if not np.isfinite(cube).all():
                    raise ValueError(f'Non-finite values in {name}')
                rgb = cube[[89, 59, 29]].transpose(1, 2, 0)
                low, high = np.percentile(rgb, [2, 98], axis=(0, 1))
                rgb = np.clip((rgb-low)/np.maximum(high-low, 1e-8), 0, 1)
                filename = f'{label.lower()}-{index+1}.png'
                image.imsave(args.output/filename, rgb)
                samples.append(dict(label=label, source=name,
                                    sha256=hashlib.sha256(raw).hexdigest(),
                                    image=f'/explorer/{filename}',
                                    mean=np.round(cube.mean(axis=(1, 2)), 3).tolist()))
    result = dict(bands=[90, 60, 30], note='Whole-patch means in original sensor units; no wavelength calibration supplied.', samples=samples)
    (args.output/'samples.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
