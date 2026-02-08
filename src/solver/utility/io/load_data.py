from pathlib import Path
from typing import List

from pandas import read_csv


def load_words(csv_file: Path) -> List[str]:
    """
    Load a list of words from a CSV file.

    The CSV file is expected to have a single column containing
    the words to be loaded.

    Args:
        csv_file: Path to the CSV file containing the words.

    Returns:
        List[str]: A list of words loaded from the file.
    """
    dataframe = read_csv(csv_file, header=None)
    return dataframe[0].str.lower().tolist()
