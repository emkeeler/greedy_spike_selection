from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import random
from pathlib import Path
from matplotlib.colors import LinearSegmentedColormap


def visualize_greedy_selection(file_path, n_select=10, output_dir="figs"):
    """create intuitive visualizations of the greedy sampling strategy results"""
    # read the CSV file
    df = pd.read_csv(file_path, header=None)

    # extract sequence names and sequences
    sequence_names = df.iloc[:, 0].values
    sequences = df.iloc[:, 1:].values

    # convert to list of sequences for our algorithm
    seq_list = [list(row) for row in sequences]
    n_sequences = len(seq_list)
    n_positions = len(seq_list[0])

    # for later comparison, select random sequences
    random_indices = random.sample(range(n_sequences), n_select)
    random_seqs = [seq_list[idx] for idx in random_indices]

    # run greedy selection
    selected_indices = []
    remaining_indices = list(range(n_sequences))
    diversity_scores = [0]  # Start with 0
    position_letters = [set() for _ in range(n_positions)]

    while len(selected_indices) < n_select:
        optimal_gain = -1
        optimal_idx = -1

        for idx in remaining_indices:
            # calculate how many new unique letters this sequence would add
            gain = 0
            for pos in range(n_positions):
                letter = seq_list[idx][pos]
                if letter not in position_letters[pos]:
                    gain += 1

            if gain > optimal_gain:
                optimal_gain = gain
                optimal_idx = idx

        # add  optimal sequence
        selected_indices.append(optimal_idx)
        remaining_indices.remove(optimal_idx)

        # update unique letters at each position
        for pos in range(n_positions):
            letter = seq_list[optimal_idx][pos]
            position_letters[pos].add(letter)

        # calculate diversity score after adding this sequence
        total_unique = sum(len(letters) for letters in position_letters)
        diversity_scores.append(total_unique)

    # obtain selected sequences
    selected_seqs = [seq_list[idx] for idx in selected_indices]

    # calculate random diversity for comparison
    random_diversity = []
    for i in range(n_select + 1):
        if i == 0:
            random_diversity.append(0)
        else:
            # count unique letters at each position for the random selection
            random_position_letters = [set() for _ in range(n_positions)]
            for seq in random_seqs[:i]:
                for pos in range(n_positions):
                    random_position_letters[pos].add(seq[pos])

            random_total = sum(len(letters) for letters in random_position_letters)
            random_diversity.append(random_total)

    fig = plt.figure(figsize=(6, 5))
    # 1. Diversity Score Growth
    plt.plot(
        range(n_select + 1),
        diversity_scores,
        marker="o",
        linewidth=2,
        color="black",
        label="Greedy Strategy",
    )
    plt.plot(
        range(n_select + 1),
        random_diversity,
        marker="x",
        linewidth=2,
        linestyle="--",
        color="grey",
        label="Random Selection",
    )
    plt.xlabel("Number of Sequences", fontsize=14)
    plt.ylabel("Diversity Score (Total Unique Letters)", fontsize=14)
    plt.title("Diversity Score Growth", fontsize=16)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / "diversity_score_growth.png", dpi=300, bbox_inches="tight")
    plt.show()



def visualize_all_pairwise_differences(file_path, n_select=10, info_box=True, output_dir="figs"):
    """create a visualization of pairwise differences for all sequences, highlighting selected ones"""
    # read the CSV file
    df = pd.read_csv(file_path, header=None)

    # rxtract sequence names and sequences
    sequence_names = df.iloc[:, 0].values
    sequences = df.iloc[:, 1:].values

    # convert to list of sequences for algorithm
    seq_list = [list(row) for row in sequences]
    n_sequences = len(seq_list)
    n_positions = len(seq_list[0])

    # run greedy selection
    selected_indices = []
    remaining_indices = list(range(n_sequences))
    position_letters = [Counter() for _ in range(n_positions)]

    while len(selected_indices) < n_select and remaining_indices:
        optimal_gain = -1
        optimal_idx = -1

        for idx in remaining_indices:
            # calculate how many new unique letters this sequence would add
            gain = 0
            for pos in range(n_positions):
                letter = seq_list[idx][pos]
                if position_letters[pos][letter] == 0:
                    gain += 1

            if gain > optimal_gain:
                optimal_gain = gain
                optimal_idx = idx

        # add the optimal sequence
        selected_indices.append(optimal_idx)
        remaining_indices.remove(optimal_idx)

        # update unique letters at each position
        for pos in range(n_positions):
            letter = seq_list[optimal_idx][pos]
            position_letters[pos][letter] += 1

    # create selection mask for visualization (1 for selected sequences, 0 for others)
    is_selected = np.zeros(n_sequences, dtype=bool)
    is_selected[selected_indices] = True

    # calculate pairwise differences between ALL sequences
    diff_matrix = np.zeros((n_sequences, n_sequences))

    for i in range(n_sequences):
        for j in range(n_sequences):
            # Count positions where sequences differ
            differences = sum(
                1 for pos in range(n_positions) if seq_list[i][pos] != seq_list[j][pos]
            )
            diff_matrix[i, j] = differences

    colors = plt.cm.cubehelix(np.linspace(0.2, 0.8, 256))
    cmap = LinearSegmentedColormap.from_list("cubehelix", colors)

    # generate the heatmap (manually instead of using sns.heatmap)
    fig, ax = plt.subplots(figsize=(14, 14))
    im = ax.imshow(diff_matrix, cmap=cmap, aspect="auto")

    # add colorbar
    cbar = plt.colorbar(im)
    cbar.set_label("Number of different positions")

    # add sequence labels
    ax.set_xticks(np.arange(len(sequence_names)))
    ax.set_yticks(np.arange(len(sequence_names)))
    ax.set_xticklabels(sequence_names)
    ax.set_yticklabels(sequence_names)

    # rotate x-axis labels for readability
    plt.setp(ax.get_xticklabels(), rotation=90, fontsize=9)
    plt.setp(ax.get_yticklabels(), fontsize=9)

    # add grid to simulate the heatmap grid
    ax.set_xticks(np.arange(-0.5, len(sequence_names), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(sequence_names), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=1)
    ax.tick_params(which="minor", bottom=False, left=False)

    # add bold borders around selected sequences
    for idx in selected_indices:
        # add rectangles around the selected sequences
        plt.axhline(y=idx - 0.5, color="black", linewidth=2)
        plt.axhline(y=idx + 0.5, color="black", linewidth=2)
        # Vertical lines (left and right of column)
        plt.axvline(x=idx - 0.5, color="black", linewidth=2)
        plt.axvline(x=idx + 0.5, color="black", linewidth=2)

    # add selection numbers to the selected sequences
    for i, idx in enumerate(selected_indices):
        plt.text(
            idx,
            idx,
            str(i + 1),
            ha="center",
            va="center",
            color="white",
            fontsize=14,
            fontweight="bold",
            bbox=dict(boxstyle="circle,pad=0.1", fc="black", ec="white", alpha=0.8),
        )

    plt.title("Pairwise Sequence Differences (All Sequences)", fontsize=18)

    if info_box:
        # Add a text explanation
        explanation_text = (
            "This visualization shows pairwise differences between all sequences.\n"
            f"Black squares indicate the {n_select} sequences selected by the greedy algorithm.\n"
            f"Numbers 1-{n_select} indicate the order of selection.\n\n"
            "The greedy algorithm prioritizes sequences that:\n"
            "1. Add the most new unique letters at each position\n"
            "2. Are maximally different from previously selected sequences\n\n"
            f"Average differences between all sequences: {np.mean(diff_matrix):.1f}"
        )

        plt.figtext(
            0.02,
            0.02,
            explanation_text,
            fontsize=12,
            bbox=dict(facecolor="white", alpha=0.8),
        )

    plt.tight_layout()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / "all_sequence_differences.png", dpi=300, bbox_inches="tight")
    plt.show()

    return selected_indices, sequence_names[selected_indices]
