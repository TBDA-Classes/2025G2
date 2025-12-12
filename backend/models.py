from datetime import date, datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedCollection, mapped_column, relationship
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, Any


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



########################################################################################
############################ MODELS FROM AGGREGATED DB #################################
########################################################################################

# See table descriptions in backend/scripts/create_agg_database.sql

class AggMachineActivityDaily(Base):
    """
    Example row:
    dt=2021-01-15, state_planned_down=0, state_running=8, state_unplanned_down=0
    """
    __tablename__ = "agg_machine_activity_daily"

    # PostgreSQL DATE type → Python date
    dt: Mapped[date] = mapped_column(primary_key=True)
    state_planned_down: Mapped[float] 
    state_running: Mapped[float] 
    state_unplanned_down: Mapped[float] 
    last_updated_at: Mapped[Optional[datetime]]

# Class that matches our table structure in the aggregated DB.
class AggSensorStats(Base):
    """
    Example row:
    sensor_name='TEMPERATURA_BASE', dt='2021-01-15 14:00:00', 
    min_value=20.5, avg_value=25.3, max_value=30.1, readings_count=3600
    """
    __tablename__ = "agg_sensor_stats"

    # Composite primary key: sensor_name + dt
    sensor_name: Mapped[str] = mapped_column(primary_key=True)
    # Mapped 'dt' to SQL column 'datetime' to avoid name collision
    dt: Mapped[datetime] = mapped_column(primary_key=True)
    
    min_value: Mapped[Optional[float]]
    avg_value: Mapped[Optional[float]]
    max_value: Mapped[Optional[float]]
    std_dev  : Mapped[Optional[float]]
    readings_count: Mapped[Optional[int]]
    last_updated_at: Mapped[Optional[datetime]]




class MachineUtilization(Base):
    """
    Machine utilization tracking - stores operation and downtime periods
    Example row:
    id=1, machine_state='running', state_start_time='2021-01-15 08:00:00',
    state_end_time='2021-01-15 17:00:00'
    Note: dt and duration are auto-generated columns
    """
    __tablename__ = "machine_utilization"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    machine_state: Mapped[str]
    state_start_time: Mapped[datetime]
    state_end_time: Mapped[datetime]
    # Note: dt and duration are generated columns in the database, 
    # so we don't need to define them here for inserts


class DataStatus(Base):
    """
    Example row:
    table_name='agg_machine_activity_daily', first_date=2020-12-01,
    last_date=2022-02-28, total_records=450, last_updated=2025-11-21 14:23:45
    """
    __tablename__ = "v_data_status"
    
    # Views don't have real primary keys, but SQLAlchemy requires one
    table_name: Mapped[str] = mapped_column(primary_key=True)
    first_date: Mapped[Optional[date]]
    last_date: Mapped[Optional[date]]
    total_records: Mapped[Optional[int]]
    last_updated: Mapped[Optional[datetime]]


class MachineProgramData(Base):
    """
    Machine program usage data - stores duration of each program per day
    Example row:
    id=1, dt=2021-01-15, program=123, duration_seconds=3600
    """
    __tablename__ = "machine_program_data"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    dt: Mapped[date]
    program: Mapped[int]
    duration_seconds: Mapped[int]


class AlertsDailyCount(Base):
    """
    Daily count of alerts by type
    Example row:
    day=2022-02-23, alert_type='error', amount=15
    """
    __tablename__ = "alerts_daily_count"
    
    day: Mapped[date] = mapped_column(primary_key=True)
    alert_type: Mapped[str] = mapped_column(primary_key=True)  # 'emergency', 'error', 'warning'
    amount: Mapped[int]


class AlertsDetail(Base):
    """
    Detailed alert records with timestamp and description
    Example row:
    id=1, dt='2022-02-23 14:30:00', alert_type='error', 
    alarm_code='E123', alarm_description='Motor fault'
    """
    __tablename__ = "alerts_detail"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    dt: Mapped[datetime]
    alert_type: Mapped[str]  # 'emergency', 'error', 'warning'
    alarm_code: Mapped[Optional[str]]
    alarm_description: Mapped[Optional[str]]
    raw_elem_json: Mapped[Optional[Any]] = mapped_column(JSONB)  # JSONB type



