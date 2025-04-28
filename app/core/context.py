import contextvars

current_user = contextvars.ContextVar('current_user', default=None)
