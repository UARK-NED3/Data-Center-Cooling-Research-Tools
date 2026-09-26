"""Bounded-memory aggregation of node-level M100 IPMI power records.

The output is an unassigned cluster-level workload descriptor.  It must not be
treated as a Q101 or Q102 heat input until a source documents the liquid-loop
topology and power-to-heat boundary.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import pandas as pd


def aggregate_power_chunk(frame: pd.DataFrame, frequency: str) -> pd.DataFrame:
    """Reduce one raw chunk to time-bin mean instantaneous cluster power.

    This function accepts partial-node chunks for testing and inspection.  The
    production reader first combines partial timestamp sums across all Parquet
    row groups, so a final time stamp contains every observed node record.
    """

    required = {"timestamp", "node", "value"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"IPMI power chunk is missing columns {sorted(missing)}")
    selected = frame.loc[:, ["timestamp", "node", "value"]].copy()
    selected["timestamp"] = pd.to_datetime(selected["timestamp"], utc=True)
    selected["value"] = pd.to_numeric(selected["value"], errors="coerce")
    selected = selected.dropna(subset=["timestamp", "node", "value"])
    instantaneous = (
        selected.groupby("timestamp", as_index=False)
        .agg(instantaneous_power_w=("value", "sum"), observed_node_count=("node", "size"))
        .sort_values("timestamp", kind="stable")
    )
    instantaneous["time_bin"] = instantaneous["timestamp"].dt.floor(frequency)
    return (
        instantaneous.groupby("time_bin", as_index=False)
        .agg(
            mean_observed_cluster_power_kw=("instantaneous_power_w", lambda values: values.mean() / 1000.0),
            mean_observed_node_count=("observed_node_count", "mean"),
            node_record_count=("observed_node_count", "sum"),
            timestamp_count=("timestamp", "size"),
        )
        .sort_values("time_bin", kind="stable")
        .reset_index(drop=True)
    )


def aggregate_ipmi_power_file(source_file: str | Path, frequency: str = "5min") -> pd.DataFrame:
    """Stream an IPMI Parquet file without loading all node records at once."""

    try:
        import pyarrow.parquet as pq
    except ImportError as exc:  # pragma: no cover - environment-specific guard.
        raise RuntimeError("M100 Parquet aggregation requires pyarrow") from exc
    path = Path(source_file)
    if not path.exists():
        raise FileNotFoundError(path)
    parquet = pq.ParquetFile(path)
    timestamp_sums: defaultdict[pd.Timestamp, float] = defaultdict(float)
    timestamp_counts: defaultdict[pd.Timestamp, int] = defaultdict(int)
    for index in range(parquet.num_row_groups):
        chunk = parquet.read_row_group(index, columns=["timestamp", "value"]).to_pandas()
        chunk["timestamp"] = pd.to_datetime(chunk["timestamp"], utc=True)
        chunk["value"] = pd.to_numeric(chunk["value"], errors="coerce")
        chunk = chunk.dropna(subset=["timestamp", "value"])
        partial = chunk.groupby("timestamp", sort=False)["value"].agg(["sum", "count"])
        for timestamp, values in partial.iterrows():
            timestamp_sums[timestamp] += float(values["sum"])
            timestamp_counts[timestamp] += int(values["count"])
    instantaneous = pd.DataFrame(
        {
            "timestamp": list(timestamp_sums),
            "instantaneous_power_w": [timestamp_sums[key] for key in timestamp_sums],
            "observed_node_count": [timestamp_counts[key] for key in timestamp_sums],
        }
    )
    instantaneous["time_bin"] = pd.to_datetime(instantaneous["timestamp"], utc=True).dt.floor(frequency)
    return (
        instantaneous.groupby("time_bin", as_index=False)
        .agg(
            mean_observed_cluster_power_kw=("instantaneous_power_w", lambda values: values.mean() / 1000.0),
            mean_observed_node_count=("observed_node_count", "mean"),
            node_record_count=("observed_node_count", "sum"),
            timestamp_count=("timestamp", "size"),
        )
        .sort_values("time_bin", kind="stable")
        .reset_index(drop=True)
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-file", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--frequency", default="5min")
    args = parser.parse_args(argv)
    result = aggregate_ipmi_power_file(args.source_file, args.frequency)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output_csv, index=False)
    print(
        json.dumps(
            {
                "rows": len(result),
                "start_utc": result["time_bin"].min().isoformat(),
                "end_utc": result["time_bin"].max().isoformat(),
                "median_observed_nodes": float(result["mean_observed_node_count"].median()),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
