"""Assemble a reproducible evidence record; no new model fitting or test-set claim."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from terraspectra.data import ROOT, PatchDataset
from terraspectra.model import load_model
from terraspectra.review import extraction_audit, gis_audit
from terraspectra.train import predict_loader, evaluate_scores


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', type=Path, required=True)
    args = parser.parse_args()
    torch.set_num_threads(2)
    manifest_hash = sha(ROOT/'reports/inventory.csv')
    dataset = PatchDataset('validation')
    models = []
    for week, filename, key in [('week2','hybrid_cnn.pt','cnn'),('week3','hybrid_vit.pt','transformer')]:
        report = json.loads((ROOT/f'reports/{week}/metrics.json').read_text())
        directory = ROOT/'models'/week
        fingerprints = {
            'manifest_matches': report['manifest_sha256'] == manifest_hash,
            'checkpoint_matches': report['checkpoint_sha256'] == sha(directory/filename),
            'preprocessing_matches': report['preprocessing_sha256'] == sha(directory/'preprocessing.npz'),
        }
        if not all(fingerprints.values()):
            raise ValueError(f'{week}: saved artifact fingerprint mismatch')
        model, _ = load_model(directory/filename)
        probabilities = predict_loader(model,DataLoader(dataset,batch_size=16),torch.device('cpu'))
        metrics = evaluate_scores(dataset.labels.numpy(),probabilities)
        if metrics['confusion_matrix'] != report[key]['confusion_matrix']:
            raise ValueError(f'{week}: predictions no longer reproduce the saved confusion matrix')
        models.append({'name': report['model'], 'artifact': f'models/{week}/{filename}',
                       'fingerprints': fingerprints, 'recomputed': metrics,
                       'saved_confusion_matrix_reproduced': True})
    result = {'generated_at_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'Recheck existing development evidence, not an independent test or retraining.',
              'dataset': extraction_audit(args.zip), 'models': models, 'synthetic_gis': gis_audit(),
              'previous_api_demonstration': json.loads((ROOT/'reports/week4/api_demo.json').read_text()),
              'previous_memory_audit': json.loads((ROOT/'reports/mid_review/audit.json').read_text())['memory_trials'],
              'limitations': ['Checkpoint selection used these same validation examples.',
                              'No verified source-scene grouping or independent farm test.',
                              'Map and timeline are synthetic; no chemical or forecast targets.',
                              'CPU prototype; no GPU or giant-scene throughput certification.',
                              'Previously recorded API and memory results are historical, not rerun by this command.']}
    destination = ROOT/'reports/final_review'
    destination.mkdir(parents=True,exist_ok=True)
    (destination/'evidence.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Rechecked dataset integrity, both checkpoint metrics and synthetic GIS. Evidence saved.')


if __name__ == '__main__':
    main()
