"""Tests for coverage guards on M100 system-context plots."""

from __future__ import annotations

import unittest

import pandas as pd

from benchmarks.m100_rdhx_v0_1.workload_context import select_complete_power_windows


class M100WorkloadContextTests(unittest.TestCase):
    def test_select_complete_power_windows_excludes_partial_node_coverage(self):
        frame = pd.DataFrame(
            {
                "mean_observed_cluster_power_kw": [700.0, 650.0],
                "mean_observed_node_count": [980.0, 900.0],
                "timestamp_count": [15, 15],
            }
        )

        result = select_complete_power_windows(frame, expected_nodes=980, minimum_fraction=0.98)

        self.assertEqual(result.index.tolist(), [0])


if __name__ == "__main__":
    unittest.main()
