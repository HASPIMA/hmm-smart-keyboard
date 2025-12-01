"""Validation utilities for HMM parameters."""

import numpy as np
import numpy.typing as npt

MATRIX_DIMENSION = 2


def validate_matrix(
    matrix: npt.NDArray[np.float64],
    name: str = "Matrix",
) -> None:
    """
    Validate that a matrix has the correct shape and properties.

    Args:
        matrix: Matrix to validate
        name: Name of the matrix for error messages

    Raises:
        ValueError: If matrix is invalid

    """
    if not isinstance(matrix, np.ndarray):
        msg = f"{name} must be a numpy array"
        raise TypeError(msg)

    if matrix.ndim != MATRIX_DIMENSION:
        msg = f"{name} must be {MATRIX_DIMENSION}-dimensional"
        raise ValueError(msg)

    if matrix.shape[0] == 0 or matrix.shape[1] == 0:
        msg = f"{name} cannot be empty"
        raise ValueError(msg)


def validate_probabilities(
    probs: npt.NDArray[np.float64] | list[float],
    name: str = "Probabilities",
    allow_zero: bool = True,  # noqa: FBT001, FBT002
) -> None:
    """
    Validate that values represent valid probabilities.

    Args:
        probs: Probability values to validate
        name: Name for error messages
        allow_zero: Whether to allow zero probabilities

    Raises:
        ValueError: If probabilities are invalid

    """
    probs = np.array(probs)

    if np.any(probs < 0):
        msg = f"{name} cannot contain negative values"
        raise ValueError(msg)

    if not allow_zero and np.any(probs == 0):
        msg = f"{name} cannot contain zero values"
        raise ValueError(msg)

    if np.any(probs > 1):
        msg = f"{name} cannot contain values greater than 1"
        raise ValueError(msg)


def validate_stochastic_matrix(
    matrix: npt.NDArray[np.float64],
    axis: int = 1,
    tolerance: float = 1e-6,
    name: str = "Matrix",
) -> None:
    """
    Validate that a matrix is stochastic (rows or columns sum to 1).

    Args:
        matrix: Matrix to validate
        axis: Axis along which to check sum (1 for rows, 0 for columns)
        tolerance: Tolerance for floating point comparison
        name: Name of the matrix for error messages

    Raises:
        ValueError: If matrix is not stochastic

    """
    validate_matrix(matrix, name)
    validate_probabilities(matrix, name)

    sums = np.sum(matrix, axis=axis)
    if not np.allclose(sums, 1.0, atol=tolerance):
        msg = (
            f"{name} is not stochastic: "
            f"{'rows' if axis == 1 else 'columns'} do not sum to 1"
        )
        raise ValueError(
            msg,
        )


def validate_dimensions_match(
    arr1: npt.NDArray[np.float64],
    arr2: npt.NDArray[np.float64],
    dim1: int,
    dim2: int,
    name1: str = "Array 1",
    name2: str = "Array 2",
) -> None:
    """
    Validate that specified dimensions of two arrays match.

    Args:
        arr1: First array
        arr2: Second array
        dim1: Dimension of first array to check
        dim2: Dimension of second array to check
        name1: Name of first array for error messages
        name2: Name of second array for error messages

    Raises:
        ValueError: If dimensions don't match

    """
    if arr1.shape[dim1] != arr2.shape[dim2]:
        msg = (
            f"{name1} dimension {dim1} (size {arr1.shape[dim1]}) "
            f"does not match {name2} dimension {dim2} (size {arr2.shape[dim2]})"
        )
        raise ValueError(
            msg,
        )
