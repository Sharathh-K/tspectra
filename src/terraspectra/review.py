"""Reproducible mid-project audit. Run from the repository root; no retraining."""
import argparse
import hashlib
import json
import platform
import resource
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone
from collections import Counter
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_bounds, rowcol, xy
import torch
from torch import nn
from torch.utils.data import DataLoader

from terraspectra.data import ROOT, PatchDataset, read_inventory
from terraspectra.model import HybridCNN

MIB = 1024 ** 2


def memory_trial(batch_size):
    """Use a fresh process per size so earlier trials cannot inflate its peak."""
    torch.manual_seed(42)
    torch.set_num_threads(2)
    started = time.perf_counter()
    dataset = PatchDataset('train')
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    model = HybridCNN()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    losses = []
    for step, (inputs, labels) in enumerate(loader):
        optimizer.zero_grad(set_to_none=True)
        loss = nn.CrossEntropyLoss()(model(inputs), labels)
        if not torch.isfinite(loss):
            raise ValueError('Non-finite training loss')
        loss.backward()
        if not all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters()):
            raise ValueError('Non-finite gradient')
        optimizer.step()
        losses.append(float(loss.detach()))
        if step == 2:
            break
    # macOS reports bytes; Linux reports KiB. Includes Python, libraries and data.
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak_mib = rss / MIB if sys.platform == 'darwin' else rss / 1024
    return {'batch_size': batch_size, 'steps': len(losses), 'losses': losses,
            'input_shape': list(inputs.shape), 'input_mib': inputs.numel()*inputs.element_size()/MIB,
            'cached_train_mib': dataset.inputs.numel()*dataset.inputs.element_size()/MIB,
            'peak_process_rss_mib': peak_mib, 'seconds': time.perf_counter()-started,
            'finite_loss_and_gradients': True}


def extraction_audit(zip_path):
    """Stream one ZIP member at a time; compare SHA-256 with the extracted TIFF."""
    rows = read_inventory()
    manifest = {r['path']: r for r in rows}
    checked, band_counts, crs_counts = 0, Counter(), Counter()
    with zipfile.ZipFile(zip_path) as archive:
        members = [info for info in archive.infolist() if info.filename.lower().endswith(('.tif', '.tiff'))]
        if len(members) != len(manifest) or {m.filename for m in members} != set(manifest):
            raise ValueError('ZIP and manifest file counts differ')
        for member in members:
            name = member.filename
            if name not in manifest:
                raise ValueError(f'Unexpected ZIP member: {name}')
            row = manifest[name]
            with archive.open(member) as handle:
                zipped_hash = hashlib.file_digest(handle, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else stream_hash(handle)
            raw_path = ROOT / 'data/raw' / name
            with raw_path.open('rb') as handle:
                extracted_hash = stream_hash(handle)
            if zipped_hash != extracted_hash or extracted_hash != row['sha256']:
                raise ValueError(f'File integrity mismatch: {name}')
            cube = np.load(ROOT/'data/processed'/row['processed_path'], allow_pickle=False, mmap_mode='r')
            if cube.shape != (64,64,16) or cube.dtype != np.float32 or not np.isfinite(cube).all():
                raise ValueError(f'Unexpected processed cube: {name}')
            with rasterio.open(raw_path) as src:
                band_counts[str(src.count)] += 1
                crs_counts[str(src.crs.to_epsg() if src.crs else None)] += 1
            checked += 1
    hashes_by_split = {}
    for row in rows:
        hashes_by_split.setdefault(row['split'], set()).add(row['sha256'])
    overlaps = {f'{a} / {b}': len(hashes_by_split[a] & hashes_by_split[b])
                for a in hashes_by_split for b in hashes_by_split if a < b}
    with Path(zip_path).open('rb') as handle:
        archive_hash = stream_hash(handle)
    return {'files_checked': checked, 'zip_sha256': archive_hash,
            'raw_band_counts': dict(band_counts), 'recognized_epsg_counts': dict(crs_counts),
            'split_counts': dict(Counter(r['split'] for r in rows)),
            'exact_duplicate_hash_overlap': overlaps, 'integrity_passed': True,
            'processed_shape': [64,64,16], 'processed_dtype': 'float32',
            'scope': 'Exact-byte checks cannot rule out neighbouring-patch or source-image leakage.'}


def stream_hash(handle):
    digest = hashlib.sha256()
    for block in iter(lambda: handle.read(1024*1024), b''):
        digest.update(block)
    return digest.hexdigest()


def gis_audit():
    """Check south-up JSON rows against Rasterio's north-down raster convention."""
    grid = json.loads((ROOT/'frontend/public/mock-heatmap.json').read_text())
    farm = json.loads((ROOT/'frontend/src/demo-farm.json').read_text())
    ring = farm['features'][0]['geometry']['coordinates'][0]
    west,south,east,north = grid['bounds']
    if not np.isfinite(grid['bounds']).all() or not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise ValueError('Invalid geographic bounds')
    expected_ring = [[west,south],[east,south],[east,north],[west,north],[west,south]]
    if ring != expected_ring or grid['crs'] != 'EPSG:4326' or grid['is_mock'] is not True:
        raise ValueError('Farm boundary / grid CRS or mock provenance mismatch')
    rows, columns = grid['rows'], grid['columns']
    transform = from_bounds(west,south,east,north,columns,rows)
    positions, ids, errors = set(), set(), []
    for cell in grid['cells']:
        r,c = cell['row'],cell['column']
        if not np.isfinite(cell['bounds']).all() or not np.isfinite(cell['score']) or not 0 <= cell['score'] <= 1:
            raise ValueError('Non-finite cell bounds or invalid score')
        if not (0 <= r < rows and 0 <= c < columns) or (r,c) in positions or cell['id'] in ids:
            raise ValueError('Missing, repeated or invalid grid position')
        positions.add((r,c)); ids.add(cell['id'])
        # Rasterio row zero is north. Our mock JSON row zero is south.
        raster_row = rows-1-r
        left,top = xy(transform,raster_row,c,offset='ul')
        right,bottom = xy(transform,raster_row,c,offset='lr')
        error = float(np.max(np.abs(np.array(cell['bounds'])-[left,bottom,right,top])))
        errors.append(error)
        x,y = xy(transform,raster_row,c)
        if rowcol(transform,x,y) != (raster_row,c) or error > 1e-9:
            raise ValueError('Cell corner / center round-trip failed')
    if len(positions) != rows*columns:
        raise ValueError('Incomplete grid coverage')
    return {'cells_checked': len(positions), 'max_corner_error_degrees': max(errors),
            'tolerance_degrees': 1e-9, 'boundary_matches': True, 'center_roundtrips_passed': True,
            'grid_alignment_passed': True, 'crs': 'EPSG:4326',
            'real_farm_alignment': 'NOT VALIDATED: synthetic boundary, no surveyed control points',
            'browser_camera_alignment': 'NOT VERIFIED: requires live Mapbox pan/zoom/tilt check',
            'row_convention': 'Mock rows start south; raster rows start north.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', type=Path)
    parser.add_argument('--trial', type=int, choices=[1,8,16,32])
    args = parser.parse_args()
    if args.trial:
        print(json.dumps(memory_trial(args.trial)))
        return
    if args.zip is None:
        parser.error('--zip is required for the full audit')
    report = {'schema_version': 1, 'generated_at_utc': datetime.now(timezone.utc).isoformat(), 'environment': {'python': platform.python_version(),
              'torch': torch.__version__, 'platform': platform.platform(), 'device': 'CPU'},
              'extraction': extraction_audit(args.zip), 'gis': gis_audit(), 'memory_trials': []}
    for size in [1,8,16,32]:
        result = subprocess.run([sys.executable,'-m','terraspectra.review','--trial',str(size)],
                                cwd=ROOT, capture_output=True,text=True,check=True)
        report['memory_trials'].append(json.loads(result.stdout))
    report['memory_scope'] = ('Fresh CPU process per batch, three optimizer steps, all 480 training inputs cached. '
                              'Peak RSS includes runtime and libraries; input bytes are not total memory. '
                              'No GPU or full-resolution satellite-cube capacity claim.')
    report['recommended_batch_size'] = 16
    text = json.dumps(report,indent=2)+'\n'
    (ROOT/'reports/mid_review/audit.json').write_text(text)
    (ROOT/'frontend/public/mid-review.json').write_text(text)
    print(text)


if __name__ == '__main__':
    main()
