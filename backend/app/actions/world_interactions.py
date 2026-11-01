
from dataclasses import dataclass

from app.game_state import InventoryItem
from app.game_state_manager import GameStateManager
from app.world_state_manager import WorldStateManager


@dataclass
class InteractionResult:
    success: bool
    message: str
    item_id: str | None = None


def pick_up_item(
    character_id: str,
    item_id: str,
    game_manager: GameStateManager,
    world_manager: WorldStateManager,
    max_distance: float = 2.0,
) -> InteractionResult:
    """
    Перемещает предмет из игрового мира в инвентарь.

    Сначала проверяет возможность подбора.
    Предмет удаляется из мира только после успешного
    добавления в инвентарь.
    """

    if max_distance < 0:
        return InteractionResult(False, "Некорректная дистанция подбора")

    try:
        character = game_manager.get_character(character_id)
    except ValueError:
        return InteractionResult(False, "Персонаж не найден")

    if not character.is_alive:
        return InteractionResult(False, "Персонаж мёртв")

    if not character.is_conscious:
        return InteractionResult(False, "Персонаж без сознания")

    if character.is_restrained:
        return InteractionResult(False, "Персонаж скован")

    try:
        item = world_manager.get_item(item_id)
    except ValueError:
        return InteractionResult(False, "Предмет отсутствует в мире")

    if not item.is_accessible:
        return InteractionResult(False, "Предмет недоступен")

    distance = world_manager.calculate_distance(
        character.position,
        item.position,
    )

    if distance > max_distance:
        return InteractionResult(False, "Предмет слишком далеко")

    inventory_item = InventoryItem(
        item_id=item.item_id,
        name=item.name,
        quantity=item.quantity,
        weight=item.weight,
        description=item.description,
    )

    try:
        game_manager.add_item(character_id, inventory_item)
    except Exception as exc:
        return InteractionResult(
            False,
            f"Не удалось добавить предмет в инвентарь: {exc}",
        )

    try:
        world_manager.remove_item(item_id)
    except Exception:
        game_manager.remove_item(
            character_id,
            item_id,
            item.quantity,
        )
        raise

    return InteractionResult(
        success=True,
        message=f"Предмет «{item.name}» подобран",
        item_id=item.item_id,
    )
