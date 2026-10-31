from app.engine.attributes import get_modifier
from app.engine.dice import roll_die
from app.engine.combat.models import Combatant, CombatState


def roll_initiative(combatant: Combatant) -> int:
    """Бросок инициативы: D20 + модификатор Ловкости."""
    return roll_die(20) + get_modifier(combatant.dexterity)


def start_combat(combatants: list[Combatant]) -> CombatState:
    """Определяет инициативу и создаёт состояние боя."""
    if not combatants:
        raise ValueError("В бою должен участвовать хотя бы один боец.")

    if not any(c.side == "player" and c.is_alive for c in combatants):
        raise ValueError("В бою должен быть живой игрок.")

    if not any(c.side == "enemy" and c.is_alive for c in combatants):
        raise ValueError("В бою должен быть живой противник.")

    for combatant in combatants:
        if combatant.hp < 0 or combatant.max_hp <= 0:
            raise ValueError("Некорректные показатели здоровья.")

        combatant.initiative = roll_initiative(combatant)

    # При равенстве инициативы преимущество у игрока.
    ordered = sorted(
        combatants,
        key=lambda c: (c.initiative, c.side == "player"),
        reverse=True,
    )

    return CombatState(
        id="combat_1",
        combatants=ordered,
        round_number=1,
        current_turn_index=0,
        status="active",
    )
