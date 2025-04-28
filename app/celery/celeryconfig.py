# celeryconfig.py

# Task settings
task_serializer = 'pickle'
result_serializer = 'pickle'
accept_content = ['pickle', 'json']
task_acks_late = True  # Ensure tasks are acknowledged only after they're complete
result_expires = 200
result_persistent = True

timezone = 'UTC'
enable_utc = True
task_track_started = True

# Worker settings
worker_prefetch_multiplier = 1  # For better task distribution
worker_send_task_events = False

broker_connection_retry_on_startup = True
