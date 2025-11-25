from django.contrib.contenttypes.models import ContentType
from .models import ActivityLog


def log_changes(request, instance, old_data, changed_fields):
    """
    Utility to create log activity entries for any model update.
    """
    for field in changed_fields:
        old_value = old_data[field]
        new_value = getattr(instance, field)

        ActivityLog.objects.create(
            user=request.user,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id,
            action=f"Field '{field}' changed by {request.user.username} from '{old_value}' to '{new_value}'"
        )
