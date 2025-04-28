from app.db.models import Organization
from app.db.services import CRUDBase
from app.schema.organization import OrganizationUpdate, OrganizationCreate


class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationUpdate]):
    pass


organization_crud = CRUDOrganization(Organization)
