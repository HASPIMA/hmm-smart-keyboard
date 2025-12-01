"""Distance calculation utilities for keyboard layout."""

import numpy as np
import numpy.typing as npt


def euclidean_distance(
    pos1: tuple[float, float],
    pos2: tuple[float, float],
) -> float:
    """
    Calculate Euclidean distance between two points.

    Args:
        pos1: First position as (x, y) tuple
        pos2: Second position as (x, y) tuple

    Returns:
        Euclidean distance between points

    """
    return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


def manhattan_distance(
    pos1: tuple[float, float],
    pos2: tuple[float, float],
) -> float:
    """
    Calculate Manhattan distance between two points.

    Args:
        pos1: First position as (x, y) tuple
        pos2: Second position as (x, y) tuple

    Returns:
        Manhattan distance between points

    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def get_nearby_keys(
    key_position: tuple[float, float],
    keyboard_layout: dict[str, tuple[float, float]],
    max_distance: float = 1.5,
) -> list[tuple[str, float]]:
    """
    Get keys within a certain distance of a given key position.

    Args:
        key_position: Position to check around
        keyboard_layout: Dictionary mapping keys to positions
        max_distance: Maximum distance to consider

    Returns:
        List of (key, distance) tuples for nearby keys

    """
    nearby = []
    for key, pos in keyboard_layout.items():
        dist = euclidean_distance(key_position, pos)
        if dist <= max_distance:
            nearby.append((key, dist))

    # Sort by distance
    nearby.sort(key=lambda x: x[1])
    return nearby


def calculate_distance_matrix(
    keyboard_layout: dict[str, tuple[float, float]],
) -> npt.NDArray[np.float64]:
    """
    Calculate pairwise distance matrix for all keys in a keyboard layout.

    Args:
        keyboard_layout: Dictionary mapping keys to positions

    Returns:
        Distance matrix where element [i,j] is distance between key i and key j

    """
    keys = sorted(keyboard_layout.keys())
    n = len(keys)
    distance_matrix = np.zeros((n, n))

    for i, key1 in enumerate(keys):
        for j, key2 in enumerate(keys):
            if i != j:
                distance_matrix[i, j] = euclidean_distance(
                    keyboard_layout[key1],
                    keyboard_layout[key2],
                )

    return distance_matrix
