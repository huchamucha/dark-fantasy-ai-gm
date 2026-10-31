from app.engine.combat.models import CombatState


def advance_turn(combat: CombatState) -> CombatState:
    """Передаёт ход следующему живому бойцу."""

    if combat.status != "active":
        raise ValueError("Бой уже завершён.")

    if not combat.combatants:
        raise ValueError("В бою нет участников.")

    players_alive = any(
        c.side == "player" and c.is_alive
        for c in combat.combatants
    )
    enemies_alive = any(
        c.side == "enemy" and c.is_alive
        for c in combat.combatants
    )

    if not players_alive:
        combat.status = "defeat"
        return combat

    if not enemies_alive:
        combat.status = "victory"
        return combat

    total = len(combat.combatants)

    # Ищем следующего живого участника.
    for step in range(1, total + 1):
        next_index = (combat.current_turn_index + step) % total

        if combat.combatants[next_index].is_alive:

            if next_index <= combat.current_turn_index:
                combat.round_number += 1

            combat.current_turn_index = next_index

            # Восстанавливаем действия в начале хода.
            next_combatant = combat.combatants[next_index]
            next_combatant.action_used = False
            next_combatant.bonus_action_used = False
            next_combatant.reaction_used = False
            next_combatant.movement_remaining = next_combatant.movement_speed
            
            return combat

    return combat
