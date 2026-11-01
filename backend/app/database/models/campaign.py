
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class CampaignRecord(Base):
    """Отдельное прохождение внутри выбранной игровой вселенной."""

    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)

    story_pack_id: Mapped[str] = mapped_column(
        ForeignKey("story_packs.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    story_pack_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    setting: Mapped[str] = mapped_column(String(100), nullable=False)
    tone: Mapped[str] = mapped_column(String(100), nullable=False)

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="active",
    )

    current_location_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    main_quest_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    world_flags: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    # Временное хранилище состояния мира для совместимости
    # с существующим игровым движком.
    world_data: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    story_pack = relationship("StoryPack", backref="campaigns")
