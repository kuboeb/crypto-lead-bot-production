"""
Модуль базы данных
"""
from .models import init_db, Application
from .queries import (
    create_application,
    get_application_by_user_id,
    user_has_application,
    mark_application_processed,
    get_all_applications,
    get_unprocessed_applications
)

__all__ = [
    'init_db',
    'Application',
    'create_application',
    'get_application_by_user_id',
    'user_has_application',
    'mark_application_processed',
    'get_all_applications',
    'get_unprocessed_applications'
]
