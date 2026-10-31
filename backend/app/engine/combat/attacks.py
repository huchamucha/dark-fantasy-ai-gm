from dataclasses import dataclass

from app.engine.attributes import get_modifier
from app.engine.dice import roll_die, roll_dice
from app.engine.combat.models import Combatant


@dataclass
class AttackResult:
    attacker: str
    target: str
    attack_roll: int
    attack_bonus: int
    total: int
    armor_class: int
    hit: bool
    critical: bool
    damage: int
    target_hp: int
    target_defeated: bool


def make_attack(
    attacker: Combatant,
    target: Combatant,
    proficient: bool = True,
) -> AttackResult:
    if not attacker.is_alive:
        raise ValueError("Павший боец не может атаковать.")

    if not target.is_alive:
        raise ValueError("Нельзя атаковать павшего противника.")

    if attacker.side == target.side:
        raise ValueError("Нельзя атаковать союзника.")

    ability_modifier = get_modifier(
        getattr(attacker, attacker.attack_ability)
    )

    proficiency = attacker.proficiency_bonus if proficient else 0
    attack_bonus = ability_modifier + proficiency

    attack_roll = roll_die(20)
    total = attack_roll + attack_bonus

    critical = attack_roll == 20
    hit = critical or (attack_roll != 1 and total >= target.armor_class)

    damage = 0

    if hit:
        if critical:
            damage = roll_dice(2, 4, ability_modifier)
        else:
            damage = roll_dice(1, 4, ability_modifier)

        damage = max(1, damage)
        target.hp = max(0, target.hp - damage)

    return AttackResult(
        attacker=attacker.name,
        target=target.name,
        attack_roll=attack_roll,
        attack_bonus=attack_bonus,
        total=total,
        armor_class=target.armor_class,
        hit=hit,
        critical=critical,
        damage=damage,
        target_hp=target.hp,
        target_defeated=not target.is_alive,
    )
