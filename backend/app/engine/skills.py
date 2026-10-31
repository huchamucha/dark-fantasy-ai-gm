from app.engine.attributes import Ability


SKILL_ABILITIES = {
    "athletics": Ability.STRENGTH,

    "acrobatics": Ability.DEXTERITY,
    "stealth": Ability.DEXTERITY,
    "sleight_of_hand": Ability.DEXTERITY,

    "endurance": Ability.CONSTITUTION,

    "history": Ability.INTELLIGENCE,
    "investigation": Ability.INTELLIGENCE,
    "arcana": Ability.INTELLIGENCE,
    "nature": Ability.INTELLIGENCE,
    "religion": Ability.INTELLIGENCE,

    "perception": Ability.WISDOM,
    "insight": Ability.WISDOM,
    "medicine": Ability.WISDOM,
    "survival": Ability.WISDOM,
    "animal_handling": Ability.WISDOM,

    "persuasion": Ability.CHARISMA,
    "deception": Ability.CHARISMA,
    "intimidation": Ability.CHARISMA,
    "performance": Ability.CHARISMA,
}


def get_skill_ability(skill: str) -> Ability:
    """Возвращает характеристику, связанную с навыком."""
    try:
        return SKILL_ABILITIES[skill]
    except KeyError:
        raise ValueError(f"Неизвестный навык: {skill}")
