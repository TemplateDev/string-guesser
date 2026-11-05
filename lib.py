def compare(string1: str, string2: str) -> float:
    length = max(len(string1), len(string2))
    if length == 0:
        return 100.0

    matching_positions = sum(
        character1 == character2
        for character1, character2 in zip(string1, string2)
    )
    return matching_positions / length * 100
