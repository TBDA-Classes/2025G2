from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# The base/parent which our models inherits from
class Base(DeclarativeBase):
    pass

class Period(Base):
    __tablename__ = "periods"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
