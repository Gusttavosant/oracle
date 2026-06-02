#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any


COLUMNS = [
    "Concurrency",
    "TTFT (s)",
    "Token-level Throughput (tok/s)",
    "Request-level Latency (s)",
    "RPS",
    "Total Throughput (tok/s)",
]


def non_null_mean(values: list[Any]) -> float | None:
    numbers = [value for value in values if isinstance(value, (int, float))]
    if not numbers:
        return None
    return mean(numbers)


def parse_run(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        payload = json.load(fh)

    aggregated = payload["aggregated_metrics"]
    requests = payload.get("individual_request_metrics", [])

    return {
        "concurrency": aggregated["num_concurrency"],
        "ttft_mean": non_null_mean([row.get("ttft") for row in requests]),
        "output_throughput_mean": aggregated.get(
            "mean_output_throughput_tokens_per_s"
        ),
        "e2e_latency_mean": non_null_mean([row.get("e2e_latency") for row in requests]),
        "rps": aggregated.get("requests_per_second"),
        "total_throughput": aggregated.get("mean_total_tokens_throughput_tokens_per_s"),
    }


def format_float(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.3f}"


def build_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| " + " | ".join(COLUMNS) + " |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["concurrency"]),
                    format_float(row["ttft_mean"]),
                    format_float(row["output_throughput_mean"]),
                    format_float(row["e2e_latency_mean"]),
                    format_float(row["rps"]),
                    format_float(row["total_throughput"]),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(COLUMNS)
        for row in rows:
            writer.writerow(
                [
                    row["concurrency"],
                    format_float(row["ttft_mean"]),
                    format_float(row["output_throughput_mean"]),
                    format_float(row["e2e_latency_mean"]),
                    format_float(row["rps"]),
                    format_float(row["total_throughput"]),
                ]
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate an Oracle-style summary from genai-bench outputs."
    )
    parser.add_argument(
        "experiment_dir",
        help="Directory containing the genai-bench JSON result files.",
    )
    args = parser.parse_args()

    experiment_dir = Path(args.experiment_dir).expanduser().resolve()
    if not experiment_dir.is_dir():
        raise SystemExit(f"Experiment directory not found: {experiment_dir}")

    rows = []
    for path in sorted(experiment_dir.glob("*.json")):
        if path.name == "experiment_metadata.json":
            continue
        rows.append(parse_run(path))

    rows.sort(key=lambda item: item["concurrency"])

    markdown = build_markdown(rows)
    markdown_path = experiment_dir / "oracle_style_summary.md"
    csv_path = experiment_dir / "oracle_style_summary.csv"

    markdown_path.write_text(markdown, encoding="utf-8")
    write_csv(rows, csv_path)

    print(f"Wrote {markdown_path}")
    print(f"Wrote {csv_path}")
    print()
    print(markdown.rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
