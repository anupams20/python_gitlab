from app.db.models import Role
from app.db.services import CRUDBase
from app.schema.role import RoleUpdate, RoleCreate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    pass


role_crud = CRUDRole(Role)
