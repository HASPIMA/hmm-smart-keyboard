"""Text processing utilities for HMM Smart Keyboard."""

import re


def normalize_text(
    text: str,
    lowercase: bool = True,
) -> str:
    """
    Normalize text by removing extra whitespace and optionally converting to lowercase.

    Args:
        text: Input text to normalize
        lowercase: Whether to convert text to lowercase

    Returns:
        Normalized text string

    """
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text.strip())

    if lowercase:
        text = text.lower()

    return text


def tokenize(
    text: str,
    by_word: bool = True,
) -> list[str]:
    """
    Tokenize text into words or characters.

    Args:
        text: Input text to tokenize
        by_word: If True, tokenize by words; if False, tokenize by characters

    Returns:
        List of tokens

    """
    if by_word:
        # Split by whitespace and punctuation
        tokens = re.findall(r"\b\w+\b", text.lower())
    else:
        # Split into individual characters (excluding whitespace)
        tokens = [char for char in text if not char.isspace()]

    return tokens


def remove_punctuation(text: str) -> str:
    """
    Remove punctuation from text.

    Args:
        text: Input text

    Returns:
        Text with punctuation removed

    """
    return re.sub(r"[^\w\s]", "", text)


def get_character_set(text: str) -> set[str]:
    """
    Extract unique characters from text.

    Args:
        text: Input text

    Returns:
        Set of unique characters

    """
    return {char.lower() for char in text if char.isalpha()}
