# utils/activity_logger.py

from django.contrib.contenttypes.models import ContentType
from website.models import ActivityLog
from django.utils import timezone


def log_changes(request, instance, old_data, changed_fields):
    """
    Log grouped changes only for status and remarks fields.
    """
    log_messages = []

    if "status" in changed_fields:
        old_value = old_data["status"]
        new_value = instance.status
        log_messages.append(
            f"Status changed from '{old_value}' to '{new_value}'")

    if "remarks" in changed_fields:
        old_value = old_data["remarks"]
        new_value = instance.remarks
        log_messages.append(f"Remarks from '{old_value}' to '{new_value}'")

    if log_messages:
        ActivityLog.objects.create(
            user=request.user,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id,
            action="\n".join(log_messages),
        )
