from app.engine.combat.models import Combatant


def move_combatant(
    combatant: Combatant,
    new_x: int,
    new_y: int,
) -> dict:
    """Перемещает бойца по условной квадратной карте."""

    if not combatant.is_alive:
        raise ValueError("Павший боец не может двигаться.")

    if new_x < 0 or new_y < 0:
        raise ValueError("Координаты не могут быть отрицательными.")

    dx = abs(new_x - combatant.x)
    dy = abs(new_y - combatant.y)

    # Диагональное движение пока стоит столько же, сколько прямое.
    distance = max(dx, dy)

    if distance > combatant.movement_remaining:
        raise ValueError("Недостаточно оставшегося движения.")

    old_x = combatant.x
    old_y = combatant.y

    combatant.x = new_x
    combatant.y = new_y
    combatant.movement_remaining -= distance

    return {
        "combatant": combatant.name,
        "old_position": (old_x, old_y),
        "new_position": (new_x, new_y),
        "distance": distance,
        "movement_remaining": combatant.movement_remaining,
    }
