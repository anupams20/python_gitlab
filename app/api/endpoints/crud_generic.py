from datetime import datetime, timezone
from typing import List, Type

from app.celery.clickhouse import process_event
from app.core.enums import EventNameEnum
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.core.enum import RoleEnum
from app.db.models import User
from app.db.services import CRUDBase
from app.decorators import rbac_validator


def get_generic_crud_routes(
    schema: Type[BaseModel],
    create_schema: Type[BaseModel],
    update_schema: Type[BaseModel],
    crud_service: CRUDBase,
    entity_name: str,
):
    router = APIRouter()

    @router.get(f"/{entity_name}/", response_model=List[schema], tags=[entity_name])
    @rbac_validator([RoleEnum.ORG_ADMIN])
    async def read_entities(
        request: Request,
        skip: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        return await crud_service.get_multi(db, skip=skip, limit=limit)

    @router.post(f"/{entity_name}/", response_model=schema, tags=[entity_name])
    @rbac_validator([RoleEnum.ORG_ADMIN])
    async def create_entity(
        request: Request,
        entity: create_schema,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        response = await crud_service.create(db, obj_in=entity)
        event_name = f"{entity_name.upper()}_CREATE"
        print(f"in_generic_crud: {event_name}")
        event = EventNameEnum.__members__.get(event_name, None)
        if event:
            process_event.delay(
                name=event,
                payload=response.to_dict(),
                timestamp=datetime.now(timezone.utc).isoformat(),
                org_id= user.organization_id,
                user_id = user.id
            )
        return response

    @router.get(
        f"/{entity_name}/{{entity_id}}", response_model=schema, tags=[entity_name]
    )
    @rbac_validator([RoleEnum.ORG_ADMIN])
    async def read_entity(
        request: Request,
        entity_id: str,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        db_entity = await crud_service.get(db=db, id=entity_id)
        if db_entity is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity_name} not found"
            )
        return db_entity

    @router.put(
        f"/{entity_name}/{{entity_id}}", response_model=schema, tags=[entity_name]
    )
    @rbac_validator([RoleEnum.ORG_ADMIN])
    async def update_entity(
        request: Request,
        entity_id: str,
        entity: update_schema,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        updated_entity = await crud_service.update(db=db, obj_in=entity)
        if updated_entity is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity_name} not found"
            )
        return updated_entity

    @router.delete(
        f"/{entity_name}/{{entity_id}}", response_model=schema, tags=[entity_name]
    )
    @rbac_validator([RoleEnum.ORG_ADMIN])
    async def delete_entity(
        request: Request,
        entity_id: str,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):

        deleted_entity = await crud_service.delete(db=db, id=entity_id)
        if deleted_entity is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity_name} not found"
            )
        return deleted_entity

    return router
