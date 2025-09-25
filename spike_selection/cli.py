from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .select import process_sequences
from .visualization import (
    visualize_all_pairwise_differences,
    visualize_greedy_selection,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select diverse sequences and optionally create visualizations.",
    )
    parser.add_argument("csv_path", help="path to the alignment csv file")
    parser.add_argument(
        "-n",
        "--n-select",
        dest="n_select",
        type=int,
        default=10,
        help="number of sequences to select",
    )
    parser.add_argument(
        "--start-with",
        nargs="+",
        default=None,
        help="identifiers to pre-select before greedy selection",
    )
    parser.add_argument(
        "--plot-greedy",
        action="store_true",
        help="generate the greedy selection growth plot",
    )
    parser.add_argument(
        "--plot-pairwise",
        action="store_true",
        help="generate the pairwise difference heatmap",
    )
    parser.add_argument(
        "--figure-dir",
        default="figs",
        help="directory where figures will be written",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)

    csv_path = Path(args.csv_path).expanduser()
    if not csv_path.is_file():
        raise FileNotFoundError(f"csv file not found: {csv_path}")

    start_with = args.start_with if args.start_with else None

    process_sequences(csv_path, n_select=args.n_select, start_with=start_with)

    figure_dir = Path(args.figure_dir)

    if args.plot_greedy or args.plot_pairwise:
        figure_dir.mkdir(parents=True, exist_ok=True)

    if args.plot_greedy:
        visualize_greedy_selection(
            csv_path,
            n_select=args.n_select,
            output_dir=figure_dir,
        )

    if args.plot_pairwise:
        visualize_all_pairwise_differences(
            csv_path,
            n_select=args.n_select,
            info_box=False,
            output_dir=figure_dir,
        )


if __name__ == "__main__":
    main()

