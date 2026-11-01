
from app.game_state import (
    CharacterState,
    GameState,
    InventoryItem,
    Position,
)
from app.actions.execution import ExecutionResult
from app.actions.combat_parry import (
    ParryResult,
    ParryStatus,
)


class GameStateManager:
    """Единый безопасный интерфейс изменения игрового состояния."""

    def __init__(self, state: GameState):
        self.state = state

    def get_character(self, character_id: str) -> CharacterState:
        """Находит игрока или NPC по ID."""

        if self.state.player.character_id == character_id:
            return self.state.player

        character = self.state.npcs.get(character_id)

        if character is None:
            raise ValueError(f"Персонаж {character_id} не найден")

        return character

    def add_item(self, character_id: str, item: InventoryItem) -> None:
        """Добавляет предмет или увеличивает его количество."""

        character = self.get_character(character_id)

        existing = next(
            (
                entry
                for entry in character.inventory
                if entry.item_id == item.item_id
            ),
            None,
        )

        if existing:
            if existing.name != item.name or existing.weight != item.weight:
                raise ValueError(
                    "Нельзя объединить предметы с разными характеристиками"
                )

            existing.quantity += item.quantity
            return

        character.inventory.append(item.model_copy(deep=True))

    def remove_item(
        self,
        character_id: str,
        item_id: str,
        quantity: int = 1,
    ) -> InventoryItem:
        """Удаляет указанное количество предмета."""

        if quantity < 1:
            raise ValueError("Количество должно быть положительным")

        character = self.get_character(character_id)

        item = next(
            (
                entry
                for entry in character.inventory
                if entry.item_id == item_id
            ),
            None,
        )

        if item is None:
            raise ValueError("Предмет отсутствует в инвентаре")

        if item.quantity < quantity:
            raise ValueError("Недостаточно предметов")

        removed = item.model_copy(deep=True)
        removed.quantity = quantity

        item.quantity -= quantity

        if item.quantity == 0:
            character.inventory.remove(item)

        return removed

    def move_character(
        self,
        character_id: str,
        position: Position,
    ) -> None:
        """Изменяет положение персонажа."""

        character = self.get_character(character_id)

        if not character.is_alive:
            raise ValueError("Мёртвый персонаж не может двигаться")

        if not character.is_conscious:
            raise ValueError("Персонаж без сознания")

        if character.is_restrained:
            raise ValueError("Персонаж скован")

        character.position = position.model_copy(deep=True)

    def spend_stamina(self, character_id: str, amount: int) -> None:
        """Расходует выносливость."""

        if amount < 0:
            raise ValueError("Расход не может быть отрицательным")

        character = self.get_character(character_id)

        if character.stamina < amount:
            raise ValueError("Недостаточно выносливости")

        character.stamina -= amount

    def apply_execution_result(
        self,
        character_id: str,
        result: ExecutionResult,
    ) -> None:
        """Применяет расходы БР и выносливости."""

        character = self.get_character(character_id)

        if result.initial_br != character.current_br:
            raise ValueError(
                "Результат исполнения рассчитан для другого значения БР"
            )

        if result.remaining_br < 0:
            raise ValueError("Остаток БР не может быть отрицательным")

        if result.remaining_br > character.current_br:
            raise ValueError("Остаток БР не может превышать исходный БР")

        if result.spent_stamina < 0:
            raise ValueError("Расход выносливости не может быть отрицательным")

        if character.stamina < result.spent_stamina:
            raise ValueError("Недостаточно выносливости")

        character.current_br = result.remaining_br
        character.stamina -= result.spent_stamina

    def apply_parry_result(
        self,
        defender_id: str,
        result: ParryResult,
    ) -> None:
        """Применяет результат парирования к состоянию защитника."""

        defender = self.get_character(defender_id)

        if not defender.is_alive:
            raise ValueError("Мёртвый персонаж не может парировать")

        if not defender.is_conscious:
            raise ValueError("Персонаж без сознания не может парировать")

        if defender.is_restrained:
            raise ValueError("Скованный персонаж не может парировать")

        if result.br_spent < 0 or result.stamina_spent < 0:
            raise ValueError("Расход ресурсов не может быть отрицательным")

        if defender.current_br < result.br_spent:
            raise ValueError("Недостаточно БР для парирования")

        if defender.stamina < result.stamina_spent:
            raise ValueError("Недостаточно выносливости для парирования")

        if result.initiative_transferred:
            if not result.success or result.status != ParryStatus.COUNTERED:
                raise ValueError(
                    "Передача инициативы возможна только после успешного "
                    "контратакующего парирования"
                )

        # Сначала проверяем всё, затем изменяем состояние.
        defender.current_br -= result.br_spent
        defender.stamina -= result.stamina_spent

        if result.initiative_transferred:
            self.transfer_initiative(defender_id)

    def start_new_turn(self) -> None:
        """Обычное начало раунда с восстановлением БР."""

        for character in [self.state.player, *self.state.npcs.values()]:
            if character.is_alive:
                character.current_br = character.max_br

        self.state.active_character_id = self.state.player.character_id
        self.state.turn_number += 1

    def transfer_initiative(self, character_id: str) -> None:
        """
        Передаёт инициативу персонажу без восстановления БР.

        Используется после успешного контратакующего парирования.
        """

        character = self.get_character(character_id)

        if not character.is_alive:
            raise ValueError("Мёртвый персонаж не может получить инициативу")

        if not character.is_conscious:
            raise ValueError(
                "Персонаж без сознания не может получить инициативу"
            )

        self.state.active_character_id = character_id
        self.state.turn_number += 1
