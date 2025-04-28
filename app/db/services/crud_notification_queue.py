from app.db.models import NotificationQueue
from app.db.services import CRUDBase
from app.schema.notification_queue import NotificationQueueCreate, NotificationQueueUpdate


class CRUDNotificationQueue(CRUDBase[NotificationQueue, NotificationQueueCreate, NotificationQueueUpdate]):
    pass


notification_queue_crud = CRUDNotificationQueue(NotificationQueue)
