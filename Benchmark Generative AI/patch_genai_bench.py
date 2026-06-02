#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path


OLD = """            # Validate that all values are valid for processing
            if not values:
                raise ValueError(
                    f"No values found for metric '{key}'. This should never happen!"
                )
"""

NEW = """            # Some providers stream in a way that makes certain metrics
            # (for example TPOT) unavailable or intentionally filtered out.
            # Keep the aggregated field empty and continue with the rest.
            if not values:
                logger.warning(
                    f"No values found for metric '{key}'. Leaving it empty for this run."
                )
                continue
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Patch genai-bench to tolerate missing aggregated metrics."
    )
    parser.add_argument(
        "venv_dir",
        help="Path to the virtualenv where genai-bench is installed.",
    )
    args = parser.parse_args()

    venv_dir = Path(args.venv_dir).expanduser().resolve()
    candidates = list(
        venv_dir.glob(
            "lib/python*/site-packages/genai_bench/metrics/aggregated_metrics_collector.py"
        )
    )
    if not candidates:
        raise SystemExit(f"aggregated_metrics_collector.py not found under {venv_dir}")

    target = candidates[0]
    content = target.read_text(encoding="utf-8")

    if NEW in content:
        print(f"Patch already present in {target}")
        return 0

    if OLD not in content:
        raise SystemExit(
            "Expected genai-bench source block not found. Patch may need updating."
        )

    target.write_text(content.replace(OLD, NEW), encoding="utf-8")
    print(f"Patched {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
