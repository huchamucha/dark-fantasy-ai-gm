
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class CharacterRecord(Base):
    """Персонаж конкретной кампании."""

    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    campaign_id: Mapped[str] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    player_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    class_name: Mapped[str] = mapped_column(String(100), nullable=False)

    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    hp: Mapped[int] = mapped_column(Integer, nullable=False)
    max_hp: Mapped[int] = mapped_column(Integer, nullable=False)

    strength: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    dexterity: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    constitution: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    intelligence: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    wisdom: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    charisma: Mapped[int] = mapped_column(Integer, nullable=False, default=10)

    proficiency_bonus: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=2,
    )

    proficient_skills: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    gold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    location_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    inventory: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    status_flags: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    notes: Mapped[dict] = mapped_column(
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

    campaign = relationship("CampaignRecord", backref="characters")
