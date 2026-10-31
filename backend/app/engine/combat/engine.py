from app.engine.combat.models import Combatant, CombatState
from app.engine.combat.turn_order import start_combat
from app.engine.combat.attacks import make_attack
from app.engine.combat.turns import advance_turn
from app.engine.combat.range import can_attack
from app.engine.combat.movement import move_combatant

class CombatEngine:
    def __init__(self):
        self.battles: dict[str, CombatState] = {}

    def start_battle(
        self,
        combatants: list[Combatant],
    ) -> CombatState:
        """Создаёт новый бой."""
        battle = start_combat(combatants)

        if battle.id in self.battles:
            raise ValueError("Бой с таким ID уже существует.")

        self.battles[battle.id] = battle
        return battle

    def attack(
        self,
        battle_id: str,
        target_id: str,
    ):
        """Атакует цель текущим участником."""
        battle = self._get_battle(battle_id)

        if battle.status != "active":
            raise ValueError("Бой уже завершён.")

        attacker = battle.current_combatant

        if attacker is None:
            raise ValueError("Сейчас нет доступного участника.")

        if attacker.action_used:
            raise ValueError("Основное действие уже использовано.")

        target = next(
            (
                c for c in battle.combatants
                if c.id == target_id
            ),
            None,
        )

        if target is None:
            raise ValueError("Цель не найдена.")

        if target.side == attacker.side:
            raise ValueError("Нельзя атаковать союзника.")

        if not target.is_alive:
            raise ValueError("Нельзя атаковать павшего противника.")

        if not can_attack(attacker, target):
            raise ValueError("Цель находится за пределами дальности оружия.")

        result = make_attack(attacker, target)

        # Даже промах расходует основное действие.
        attacker.action_used = True

        # Проверяем завершение боя.
        players_alive = any(
            c.side == "player" and c.is_alive
            for c in battle.combatants
        )
        enemies_alive = any(
            c.side == "enemy" and c.is_alive
            for c in battle.combatants
        )

        if not enemies_alive:
            battle.status = "victory"
        elif not players_alive:
            battle.status = "defeat"

        return result

        if target is None:
            raise ValueError("Цель не найдена.")

        return make_attack(attacker, target)
    
    def move(
        self,
        battle_id: str,
        new_x: int,
        new_y: int,
    ) -> dict:
        """Перемещает текущего бойца."""

        battle = self._get_battle(battle_id)

        if battle.status != "active":
            raise ValueError("Бой уже завершён.")

        combatant = battle.current_combatant

        if combatant is None:
            raise ValueError("Нет активного участника.")

        return move_combatant(combatant, new_x, new_y)
    
    def end_turn(self, battle_id: str) -> CombatState:
        """Завершает ход и передаёт управление."""
        battle = self._get_battle(battle_id)
        return advance_turn(battle)

    def get_battle_status(self, battle_id: str) -> dict:
        """Возвращает текущее состояние боя."""
        battle = self._get_battle(battle_id)

        return {
            "id": battle.id,
            "round": battle.round_number,
            "status": battle.status,
            "current_turn": (
                battle.current_combatant.name
                if battle.current_combatant
                else None
            ),
            "combatants": [
                {
                    "id": c.id,
                    "name": c.name,
                    "side": c.side,
                    "hp": c.hp,
                    "max_hp": c.max_hp,
                    "alive": c.is_alive,
                    "initiative": c.initiative,
                }
                for c in battle.combatants
            ],
        }

    def _get_battle(self, battle_id: str) -> CombatState:
        battle = self.battles.get(battle_id)

        if battle is None:
            raise ValueError("Бой не найден.")

        return battle
