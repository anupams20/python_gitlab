from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models import Base


class AuditLog(Base):
    table_name: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    old_data: Mapped[dict] = mapped_column(JSONB)
    new_data: Mapped[dict] = mapped_column(JSONB)
