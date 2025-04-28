from __future__ import annotations

from fastapi import APIRouter

from app.api.endpoints import (
    sandbox,
    tasks,
    user,
    websocket,
    events
)
from app.api.endpoints.crud_generic import get_generic_crud_routes
from app.db.services import organization_crud, role_crud
from app.schema.organization import OrganizationCreate, OrganizationOut, OrganizationUpdate
from app.schema.role import RoleCreate, RoleOut, RoleUpdate

api_router = APIRouter()

api_router.include_router(user.router, prefix="/users", tags=["Users"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(sandbox.router, prefix="/sandbox", tags=["sandbox"])
api_router.include_router(websocket.router, prefix="/websocket", tags=["websocket"])
api_router.include_router(events.router, prefix="/events", tags=["events"])

api_router.include_router(
    get_generic_crud_routes(
        OrganizationOut,
        OrganizationCreate,
        OrganizationUpdate,
        organization_crud,
        "organization",
    )
)
api_router.include_router(get_generic_crud_routes(RoleOut, RoleCreate, RoleUpdate, role_crud, "role"))
