from enum import Enum

class EventNameEnum(str, Enum):
    ORGANIZATION_CREATE = "organization_create"
    ORGANIZATION_UPDATE = "organization_update"
    ORGANIZATION_DELETE = "organization_delete"

    ROLE_CREATE = "role_create"
    ROLE_UPDATE = "role_update"
    ROLE_DELETE = "role_delete"

    COLLECTION_CREATE = "collection_create"
    COLLECTION_UPDATE = "collection_update"
    COLLECTION_DELETE = "collection_delete"

    INGESTION_CONFIGURATION_CREATE = "ingestion_configuration_create"
    INGESTION_CONFIGURATION_UPDATE = "ingestion_configuration_update"
    INGESTION_CONFIGURATION_DELETE = "ingestion_configuration_delete"

    INVOKE_LLM_RESPONSE = "invoke_llm_response"
    UPLOAD_FILE_SOURCE = "upload_file_source"
    REFRESHTOKEN_CREATE = "refreshtoken_create"

    FILESRC_CREATE = "filesrc_create"
    FILESRC_UPDATE = "filesrc_update"
    UPLOAD_FILE_TO_DATABASE = "upload_file_to_database"
    FILE_PROCESSING = "file_processing"
    SYNC_FILE = "sync_file"
    SYNC_FILE_CREATE = "sync_file_create"
    CHANNEL_CREATE = "channel_create"
    CONNECTION_CREATE = "connection_create"
    CONNECTION_UPDATE = "connection_update"
    NOTIFICATION_QUEUE_CREATE = "notification_queue_create"
    USER_CREATE = "user_create"
    GENIE_FILE_STORE_CREATE = "genie_file_store_create"
    CHUNK_CREATE = "chunk_create"