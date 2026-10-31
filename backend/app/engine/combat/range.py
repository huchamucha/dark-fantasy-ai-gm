from app.engine.combat.models import Combatant


def get_distance(first: Combatant, second: Combatant) -> int:
    """Расстояние между бойцами по квадратной сетке."""
    dx = abs(first.x - second.x)
    dy = abs(first.y - second.y)

    return max(dx, dy)


def can_attack(attacker: Combatant, target: Combatant) -> bool:
    """Проверяет, находится ли цель в пределах дальности оружия."""
    if not attacker.is_alive or not target.is_alive:
        return False

    if attacker.side == target.side:
        return False

    distance = get_distance(attacker, target)

    return distance <= attacker.weapon_range
