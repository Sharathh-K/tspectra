"""Small integration checks for real Week 2 artifacts and tensor layout."""
import csv
import json
import unittest
from pathlib import Path

import numpy as np
import torch

from terraspectra.data import ROOT, make_input, PatchDataset
from terraspectra.model import HybridCNN, load_model
from terraspectra.predict import preprocess_tiff


class WeekTwoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(2)

    def test_pooling_preserves_component_axis(self):
        cube = np.broadcast_to(np.arange(16, dtype='float32'), (64, 64, 16)).copy()
        result = make_input(cube)
        self.assertEqual(tuple(result.shape), (1, 16, 16, 16))
        np.testing.assert_array_equal(result[0, :, 0, 0], np.arange(16))
        with self.assertRaises(ValueError):
            make_input(np.zeros((64, 64, 125)))

    def test_model_backward_and_output_contract(self):
        model = HybridCNN()
        logits = model(torch.randn(2, 1, 16, 16, 16))
        self.assertEqual(tuple(logits.shape), (2, 3))
        torch.nn.functional.cross_entropy(logits, torch.tensor([0, 2])).backward()
        self.assertTrue(all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters()))

    def test_raw_inference_recipe_matches_week_one(self):
        with (ROOT / 'reports/inventory.csv').open() as handle:
            rows = list(csv.DictReader(handle))
        for count in ('125', '126'):
            row = next(r for r in rows if r['raw_bands'] == count)
            raw_path = ROOT / 'data/raw' / row['path']
            if not raw_path.exists():
                self.skipTest('Extract the local dataset to check raw TIFF inference.')
            actual = preprocess_tiff(raw_path)
            expected = np.load(ROOT / 'data/processed' / row['processed_path'])
            np.testing.assert_allclose(actual, expected, rtol=2e-4, atol=2e-4)

    def test_saved_model_reproduces_report(self):
        if not (ROOT / 'data/processed/validation').exists():
            self.skipTest('Run Week 1 preparation to reproduce validation predictions.')
        dataset = PatchDataset('validation')
        model, checkpoint = load_model(ROOT / 'models/week2/hybrid_cnn.pt')
        with torch.inference_mode():
            scores = model(dataset.inputs).softmax(1).numpy()
        self.assertEqual(checkpoint['class_names'], ['Health', 'Other', 'Rust'])
        np.testing.assert_allclose(scores.sum(axis=1), 1, atol=1e-6)
        report = json.loads((ROOT / 'reports/week2/metrics.json').read_text())
        accuracy = float((scores.argmax(1) == dataset.labels.numpy()).mean())
        self.assertAlmostEqual(accuracy, report['cnn']['accuracy'])
        with (ROOT / 'reports/week2/validation_predictions.csv').open() as handle:
            rows = list(csv.DictReader(handle))
        expected = np.array([[float(r['p_Health']), float(r['p_Other']), float(r['p_Rust'])] for r in rows])
        np.testing.assert_allclose(scores, expected, atol=2e-5, rtol=2e-5)


if __name__ == '__main__':
    unittest.main()
