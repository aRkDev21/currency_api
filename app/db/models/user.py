from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class User(Base):
    __tablename__ = 'user'

    username: Mapped[str] = mapped_column(primary_key=True)
    hashed_password: Mapped[str] = mapped_column()