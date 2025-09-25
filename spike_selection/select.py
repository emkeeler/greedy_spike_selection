from __future__ import annotations

import numpy as np
import pandas as pd
from collections import Counter
from typing import List, Tuple

def diversity_score(selected_sequences: List[List[str]]) -> int:
    """calculate diversity score: count of unique letters at each position"""
    if not selected_sequences:
        return 0

    n_positions = len(selected_sequences[0])
    total_unique = 0

    for pos in range(n_positions):
        unique_letters = set()
        for seq in selected_sequences:
            unique_letters.add(seq[pos])
        total_unique += len(unique_letters)

    return total_unique


def select_diverse_sequences(
    sequences: List[List[str]],
    n_select: int,
    sequence_names: List[str] | None = None,
    start_with: List[str] | None = None,
) -> List[int]:
    """
    select n_select sequences to maximize diversity

    Args:
        sequences: list of sequences (each sequence is a list of characters)
        n_select: number of sequences to select
        sequence_names: list of names corresponding to sequences (optional)
        start_with: list of sequence names to start the selection with (optional)

    Returns:
        indices of selected sequences
    """
    n_sequences = len(sequences)
    n_positions = len(sequences[0])

    # initialize variables
    selected_indices = []
    remaining_indices = list(range(n_sequences))
    position_letters = [Counter() for _ in range(n_positions)]

    # if start_with_sequences is provided, select those sequences first
    if start_with and sequence_names is not None:
        # create a dictionary to search indices by name
        name_to_idx = {name: idx for idx, name in enumerate(sequence_names)}

        for name in start_with:
            if name in name_to_idx:
                idx = name_to_idx[name]
                if idx in remaining_indices:
                    selected_indices.append(idx)
                    remaining_indices.remove(idx)

                    # update unique letters at each position
                    for pos in range(n_positions):
                        letter = sequences[idx][pos]
                        position_letters[pos][letter] += 1
                else:
                    print(f"Warning: {name} already selected or not found in dataset")
            else:
                print(f"Warning: {name} not found in dataset")

    # continue with greedy selection for remaining slots
    while len(selected_indices) < n_select and remaining_indices:
        optimal_gain = -1
        optimal_idx = -1

        for idx in remaining_indices:
            # calculate number of unique letters added by each sequence
            gain = 0
            for pos in range(n_positions):
                letter = sequences[idx][pos]
                if position_letters[pos][letter] == 0:
                    gain += 1

            if gain > optimal_gain:
                optimal_gain = gain
                optimal_idx = idx

        if optimal_gain <= 0 and len(selected_indices) > 0:
            print("No sequence adds diversity, using Hamming distance")
            # if no sequence adds diversity, use a secondary criterion
            optimal_distance = -1

            for idx in remaining_indices:
                total_distance = 0
                for sel_idx in selected_indices:
                    # Hamming distance (count positions with different letters)
                    distance = sum(
                        1
                        for pos in range(n_positions)
                        if sequences[idx][pos] != sequences[sel_idx][pos]
                    )
                    total_distance += distance

                if total_distance > optimal_distance:
                    optimal_distance = total_distance
                    optimal_idx = idx

        # add optimal sequence
        if optimal_idx != -1:
            selected_indices.append(optimal_idx)
            remaining_indices.remove(optimal_idx)

            # update counts for the letters in this sequence
            for pos in range(n_positions):
                letter = sequences[optimal_idx][pos]
                position_letters[pos][letter] += 1

    return selected_indices


def process_sequences(file_path, n_select=10, start_with=None) -> Tuple[List[int], List[str]]:
    """
        Process amino acid sequence alignment from a given comma-delimited CSV file, in
        which the first column refers to the sequence identifier and all subsequent columns
        refer to the amino acid present at each position
        (“A”, “R”, “N”, “D”, “C”, “E”, “Q”, ...) or “-“ (in the case of indels)

        sequences must be aligned

        args:
            file_path: path to CSV file containing sequences
            n_select: number of sequences to select
            start_with: list of sequence names to start the selection with (optional)
    """
    # read the CSV file
    df = pd.read_csv(file_path, header=None)

    sequence_names = df.iloc[:, 0].values
    sequences = df.iloc[:, 1:].values
    seq_list = [list(row) for row in sequences]
    selected_indices = select_diverse_sequences(
        seq_list, n_select, sequence_names=sequence_names, start_with=start_with
    )
    selected_names = sequence_names[selected_indices]
    selected_seqs = [seq_list[idx] for idx in selected_indices]
    score = diversity_score(selected_seqs)
    n_positions = len(seq_list[0])
    print(
        f"Selected {len(selected_indices)} sequences with diversity score {score} (max possible is {n_positions * n_select}):"
    )

    # print the selected sequences, indicating which were pre-selected
    for i, name in enumerate(selected_names):
        is_preselected = start_with and name in start_with
        prefix = "* " if is_preselected else "  "
        print(f"{prefix}{name}")

    if start_with:
        print("\n* = pre-selected sequence") 

    return selected_indices, selected_names



