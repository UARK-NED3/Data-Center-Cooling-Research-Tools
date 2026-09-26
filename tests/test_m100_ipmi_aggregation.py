"""Tests for bounded-memory aggregation of node-level M100 telemetry."""

from __future__ import annotations

import unittest

import pandas as pd

from benchmarks.m100_rdhx_v0_1.ipmi_aggregate import aggregate_power_chunk


class M100IpmiAggregationTests(unittest.TestCase):
    def test_aggregate_groups_node_power_on_a_declared_time_base(self):
        frame = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(
                    ["2022-09-01T00:00:00Z", "2022-09-01T00:00:20Z", "2022-09-01T00:00:00Z"], utc=True
                ),
                "node": ["1", "1", "2"],
                "value": [100.0, 120.0, 200.0],
            }
        )

        result = aggregate_power_chunk(frame, "5min")

        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result.loc[0, "mean_observed_node_count"], 1.5)
        self.assertEqual(result.loc[0, "node_record_count"], 3)
        self.assertAlmostEqual(result.loc[0, "mean_observed_cluster_power_kw"], 0.21)


if __name__ == "__main__":
    unittest.main()
