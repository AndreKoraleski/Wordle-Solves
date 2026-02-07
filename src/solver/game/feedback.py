from typing import List

from numpy import ndarray, uint8, zeros


# Precomputed powers of three to avoid the exponentiation operation
_POWERS_OF_THREE = [1, 3, 9, 27, 81]


def _encode_feedback(guess: str, answer: str) -> int:
    """
    Encode Wordle feedback between a guess and an answer into a base-3 integer.

    The encoding represents the feedback for each letter position using a
    ternary system:
        - 0 -> Absent: The letter does not appear in the answer or exceeds the
          number of occurrences allowed by previous matches.
        - 1 -> Present: The letter exists in the answer but in a different
          position, respecting duplicate letter rules.
        - 2 -> Correct: The letter matches the answer at the same position.

    The final encoded integer is constructed as:

        sum(feedback[i] * 3**i for i in range(5))

    This ensures a unique mapping for all possible Wordle feedback patterns.

    Args:
        guess (str): The guessed 5-letter lowercase word.
        answer (str): The target 5-letter lowercase word.

    Returns:
        int: Encoded feedback value in the range [0, 242].
    """

    counts = [0] * 26
    for character in answer:
        counts[ord(character) - 97] += 1

    result = 0
    used = [0] * 5

    # First pass — Correct position (green)
    for i in range(5):
        if guess[i] == answer[i]:
            index = ord(guess[i]) - 97
            counts[index] -= 1
            used[i] = 2
            result += 2 * _POWERS_OF_THREE[i]

    # Second pass — Present but misplaced (yellow)
    for i in range(5):
        if used[i]:
            continue

        index = ord(guess[i]) - 97

        if counts[index] > 0:
            counts[index] -= 1
            result += 1 * _POWERS_OF_THREE[i]

    return result


def _decode_feedback(feedback: uint8) -> str:
    """
    Decode a Wordle feedback integer into its positional feedback string.

    Args:
        feedback (uint8): Encoded feedback value in the range [0, 242].

    Returns:
        str:
            A 5-character string representing positional feedback using:
            'A' for absent, 'P' for present, and 'C' for correct.
    """
    result = [""] * 5

    for i in range(5):
        digit = feedback % 3

        if digit == 2:
            result[i] = "C"
        elif digit == 1:
            result[i] = "P"
        else:
            result[i] = "A"

        feedback //= 3

    return "".join(result)


def build_feedback_encode_table(
    word_bank: List[str], valid_words: List[str]
) -> ndarray:
    """
    Construct a Wordle feedback lookup table.

    This table stores the encoded feedback pattern for every combination of
    guessed word and valid answer word. The resulting matrix allows constant-time
    retrieval of feedback during solver execution.

    Args:
        word_bank (List[str]): List of all allowed guess words.
        valid_words (List[str]): List of all valid answer words.

    Returns:
        ndarray:
            A two-dimensional NumPy array of shape
            ``(len(word_bank), len(valid_words))`` with dtype ``uint8``
            for memory optimization.
    """

    number_of_guesses = len(word_bank)
    number_of_answers = len(valid_words)

    table = zeros((number_of_guesses, number_of_answers), dtype=uint8)

    for guess_index, guess in enumerate(word_bank):
        for answer_index, answer in enumerate(valid_words):
            table[guess_index, answer_index] = _encode_feedback(guess, answer)

    return table


def build_feedback_decode_table() -> List[str]:
    """
    Construct a lookup table that maps encoded feedback values to their
    decoded positional representation.

    Since Wordle feedback is encoded using a base-3 representation with
    five positions, there are exactly:

        3^5 = 243

    possible feedback values.

    This function precomputes the decoding for every possible encoded
    feedback integer, allowing constant-time lookup instead of repeated
    decoding computations.

    Returns:
        List[str]:
            A list of length 243 where index ``i`` contains the decoded
            5-character feedback string corresponding to encoded value ``i``.
    """

    table: List[str] = [""] * 243

    for i in range(243):
        table[i] = _decode_feedback(uint8(i))

    return table
