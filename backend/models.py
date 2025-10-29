from sqlalchemy.orm import DeclarativeBase, Mapped, MappedCollection, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import Optional


# IMPORTANT: 

# mapped_column(): Defines the column settings like PK, FK
# Optional[]: Column can be NULL, used when the DB says nullable for the column
# relationship(): Link tables together, to navigate between related objects
# back_populates: Two-way relationship, so both sides can access each other.


# The base/parent which our models inherits from
class Base(DeclarativeBase):
    pass

class Period(Base):
    __tablename__ = "periods"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] #Mapped[] is a type hint 


class Variable(Base):
    __tablename__ = "variable"

    id:Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    datatype: Mapped[str]

    # children: Mapped[list["Child"]] = relationship(back_populates="parent")
    variable_log_floats: Mapped[list["VariableLogFloat"]] = relationship(back_populates="variable")
    variable_log_strings: Mapped[list["VariableLogString"]] = relationship(back_populates="variable")


class VariableLogFloat(Base):
    __tablename__ = "variable_log_float"

    id_var: Mapped[int] = mapped_column(
        ForeignKey("variable.id"), 
        primary_key=True
    )
    date: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[Optional[float]]

    # parent: Mapped["Parent"] = relationship(back_populates="children")
    variable: Mapped["Variable"] = relationship(back_populates="variable_log_floats")


class VariableLogString(Base):
    __tablename__ = "variable_log_string"

    id_var: Mapped[int] = mapped_column(ForeignKey("variable.id"), primary_key=True)
    date: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[Optional[str]]

    variable: Mapped["Variable"] = relationship(back_populates="variable_log_strings")
