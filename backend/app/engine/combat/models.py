
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Combatant:
    id: str
    name: str
    side: Literal["player", "enemy"]

    hp: int
    max_hp: int
    armor_class: int

    strength: int = 10
    dexterity: int = 10
    constitution: int = 10

    proficiency_bonus: int = 2
    initiative: int = 0

    weapon_name: str = "Безоружный удар"
    weapon_dice: str = "1d4"
    attack_ability: str = "strength"
    weapon_range: int = 1

    conditions: list[str] = field(default_factory=list)
    action_used: bool = False
    bonus_action_used: bool = False
    reaction_used: bool = False
    x: int = 0
    y: int = 0
    movement_speed: int = 9
    movement_remaining: int = 9
    @property
    def is_alive(self) -> bool:
        return self.hp > 0


@dataclass
class CombatState:
    id: str
    combatants: list[Combatant] = field(default_factory=list)

    round_number: int = 1
    current_turn_index: int = 0

    status: Literal["active", "victory", "defeat"] = "active"

    @property
    def current_combatant(self) -> Combatant | None:
        alive = [
            combatant
            for combatant in self.combatants
            if combatant.is_alive
        ]

        if not alive:
            return None

        if self.current_turn_index >= len(self.combatants):
            return None

        combatant = self.combatants[self.current_turn_index]

        return combatant if combatant.is_alive else None
