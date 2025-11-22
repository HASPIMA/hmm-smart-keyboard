"""Probability calculation utilities for HMM."""

import numpy as np
import numpy.typing as npt


def log_probability(prob: float) -> float:
    """
    Calculate log probability, handling zero probabilities.

    Args:
        prob: Probability value (0 to 1)

    Returns:
        Log probability, or negative infinity for zero probability
    """
    if prob == 0:
        return float('-inf')
    return np.log(prob)


def normalize_probabilities(
    probs: npt.NDArray[np.float64] | list[float],
) -> npt.NDArray[np.float64]:
    """
    Normalize a probability distribution to sum to 1.

    Args:
        probs: Array or list of probability values

    Returns:
        Normalized probability array

    Raises:
        ValueError: If all probabilities are zero
    """
    probs = np.array(probs, dtype=float)
    total = np.sum(probs)

    if total == 0:
        raise ValueError('Cannot normalize: all probabilities are zero')

    return probs / total


def add_log_probabilities(
    log_prob1: float,
    log_prob2: float,
) -> float:
    """
    Add two log probabilities using the log-sum-exp trick.

    Args:
        log_prob1: First log probability
        log_prob2: Second log probability

    Returns:
        Log of the sum of probabilities
    """
    if log_prob1 == float('-inf'):
        return log_prob2
    if log_prob2 == float('-inf'):
        return log_prob1

    # log(exp(a) + exp(b)) = max + log(exp(a-max) + exp(b-max))
    max_log = max(log_prob1, log_prob2)
    return max_log + np.log(np.exp(log_prob1 - max_log) + np.exp(log_prob2 - max_log))


def exp_normalize(
    log_probs: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    """
    Convert log probabilities to normalized probabilities.

    Args:
        log_probs: Array of log probabilities

    Returns:
        Normalized probability array
    """
    # Subtract max for numerical stability
    max_log = np.max(log_probs)
    if max_log == float('-inf'):
        return np.zeros_like(log_probs)

    exp_probs = np.exp(log_probs - max_log)
    return exp_probs / np.sum(exp_probs)
