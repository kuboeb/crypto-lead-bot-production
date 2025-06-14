"""
Модуль базы данных
"""
from .models import init_db, Application, UnfinishedApplication, Review, Referral
from .queries import (
    create_application,
    get_application_by_user_id,
    user_has_application,
    mark_application_processed,
    get_all_applications,
    get_unprocessed_applications,
    save_unfinished_application,
    get_unfinished_applications_for_reminder,
    mark_reminder_sent,
    get_recent_applications_count,
    get_recent_applications,
    get_random_reviews,
    add_review,
    save_referral,
    get_user_referrals_count,
    get_referrer_by_user_id
)

__all__ = [
    'init_db',
    'Application',
    'UnfinishedApplication',
    'Review',
    'create_application',
    'get_application_by_user_id',
    'user_has_application',
    'mark_application_processed',
    'get_all_applications',
    'get_unprocessed_applications',
    'save_unfinished_application',
    'get_unfinished_applications_for_reminder',
    'mark_reminder_sent',
    'get_recent_applications_count',
    'get_recent_applications',
    'get_random_reviews',
    'add_review',
    'save_referral',
    'get_user_referrals_count',
    'get_referrer_by_user_id',
    'Referral'
]
