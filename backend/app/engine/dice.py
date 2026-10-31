import random

ALLOWED_DICE = {4, 6, 8, 10, 12, 20}


def roll_die(sides: int, rng=None) -> int:
    """Бросает один кубик."""
    if sides not in ALLOWED_DICE:
        raise ValueError(f"Недопустимый кубик: D{sides}")

    roller = rng if rng is not None else random.SystemRandom()
    return roller.randint(1, sides)


def roll_dice(count: int, sides: int, modifier: int = 0, rng=None) -> int:
    """Бросает несколько кубиков и прибавляет модификатор."""
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        raise ValueError("Количество кубиков должно быть положительным числом")

    return sum(roll_die(sides, rng) for _ in range(count)) + modifier
