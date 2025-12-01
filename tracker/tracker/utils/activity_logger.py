from django.contrib.contenttypes.models import ContentType
from .models import ActivityLog


def log_changes(request, instance, old_data, changed_fields):
    """
    Log all changed fields in a single entry instead of multiple logs.
    """

    changes_summary = []

    for field in changed_fields:
        old_value = old_data[field]
        new_value = getattr(instance, field)
        changes_summary.append(f"{field}: '{old_value}' → '{new_value}'")

    summary_text = ", ".join(changes_summary)

    ActivityLog.objects.create(
        user=request.user,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.id,
        action=f"Updated by {request.user.username}: {summary_text}"
        print("LOG CREATED:", summary_text)

    )
