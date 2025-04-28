import uuid
from datetime import datetime

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import event, insert
from sqlalchemy.orm import ORMExecuteState, Session
from sqlalchemy.sql import Executable

from app.core.context import current_user
from app.core.enum import RoleEnum
from app.core.logging import AppLogger
from app.db.models import AuditLog, Base

logger = AppLogger().get_logger()


def orm_to_dict(orm_obj):
    return {
        column.name: (
            getattr(orm_obj, column.name).isoformat()
            if isinstance(getattr(orm_obj, column.name), datetime)
            else getattr(orm_obj, column.name)
        )
        for column in orm_obj.__table__.columns
    }


def audit_insert(mapper, connection, target):
    # Log data for an INSERT operation
    new_data = orm_to_dict(target)
    log_entry = AuditLog(
        id=str(uuid.uuid4()),
        table_name=target.__tablename__,
        action="INSERT",
        new_data=new_data,
        # No need to serialize, will be auto-converted to JSONB
        created_by="system",  # Fetch from context or authentication
    )
    connection.execute(insert(AuditLog).values(orm_to_dict(log_entry)))


def audit_update(mapper, connection, target):
    # Log data for an UPDATE operation
    old_data = (
        connection.execute(
            target.__table__.select().where(target.__table__.c.id == target.id)
        )
        .mappings()
        .one()
    )
    new_data = new_data = orm_to_dict(target)
    log_entry = AuditLog(
        id=str(uuid.uuid4()),
        table_name=target.__tablename__,
        action="UPDATE",
        old_data=dict(jsonable_encoder(old_data)),
        # Store old data as JSONB
        new_data=new_data,  # Store new data as JSONB
        created_by="system",
    )

    connection.execute(insert(AuditLog).values(orm_to_dict(log_entry)))


def audit_delete(mapper, connection, target):
    # Log data for a DELETE operation
    old_data = orm_to_dict(target)
    log_entry = AuditLog(
        id=str(uuid.uuid4()),
        table_name=target.__tablename__,
        action="DELETE",
        old_data=old_data,  # Store old data as JSONB
        created_by="system",
    )
    connection.execute(insert(AuditLog).values(orm_to_dict(log_entry)))


def set_user_fields(mapper, connection, target):
    user = current_user.get()
    if not user:
        return False
    if target.created_by is None:
        target.created_by = user.id
    if target.updated_by is None:
        target.updated_by = user.id
    if (
        hasattr(target, "organization_id")
        and target.organization_id != user.organization_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Organization mismatch"
        )


def filter_by_organization_id(statement: Executable) -> Executable:
    user = current_user.get()
    if not user:
        return statement

    if user.role.name in (RoleEnum.SUPER_ADMIN):
        return statement

    query_entity = statement.column_descriptions[0]["entity"]
    if not hasattr(query_entity, "__table__"):
        return statement

    table = query_entity.__table__
    if table.name == "organization":
        return statement

    if "organization_id" not in [col.name for col in table.columns]:
        return statement

    if "organization_id" in [col.name for col in table.columns]:
        statement = statement.where(table.c.organization_id == user.organization_id)

    return statement


def _do_orm_execute(orm_execute_state: ORMExecuteState):
    if orm_execute_state.is_select:
        orm_execute_state.statement = filter_by_organization_id(
            orm_execute_state.statement
        )


# Function to automatically attach listeners to all models inheriting from Base
def register_listeners():
    event.listen(Session, "do_orm_execute", _do_orm_execute)
    for cls in Base.__subclasses__():
        event.listen(cls, "before_insert", set_user_fields)
        event.listen(cls, "before_update", set_user_fields)
        event.listen(cls, "after_insert", audit_insert)
        event.listen(cls, "after_update", audit_update)
        event.listen(cls, "after_delete", audit_delete)
