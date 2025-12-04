from django.contrib.contenttypes.models import ContentType
from website.models import ActivityLog
from django.utils.text import Truncator


MAX_SUMMARY_LENGTH = 240
MAX_FIELD_VALUE_LENGTH = 30  # Truncate individual values to keep the summary short


def log_changes(request, instance, old_data, changed_fields):

    changes_summary = []

    # Define the newline separator for the log entry
    SEPARATOR = "\n"

    for field in changed_fields:
        old_value = old_data[field]
        new_instance_field_value = getattr(instance, field)

        old_display = str(old_value).strip() if old_value else ''

        # --- Determine the Display Value for the NEW field ---
        if field == 'responsible':
            try:
                # If it's a ForeignKey object (e.g., User object)
                new_display = new_instance_field_value.username if new_instance_field_value else 'N/A'
            except AttributeError:
                # If it's a CharField string
                new_display = str(
                    new_instance_field_value) if new_instance_field_value else 'N/A'
        else:
            new_display = str(new_instance_field_value).strip(
            ) if new_instance_field_value else ''

        # --- Truncate both old and new values for safety ---
        if field == 'remarks':
            # Truncate remarks heavily (e.g., to 50 characters)
            truncated_old = Truncator(old_display).chars(50)
            truncated_new = Truncator(new_display).chars(50)

            changes_summary.append(
                f"Remarks: OLD: '{truncated_old}' → NEW: '{truncated_new}'")
        else:
            # Truncate all other field changes
            truncated_old = Truncator(old_display).chars(
                MAX_FIELD_VALUE_LENGTH)
            truncated_new = Truncator(new_display).chars(
                MAX_FIELD_VALUE_LENGTH)
            changes_summary.append(
                f"{field}: '{truncated_old}' → '{truncated_new}'")

    # Join changes with a newline character
    summary_text = SEPARATOR.join(changes_summary)

    # --- Final Truncation ---
    # Ensure the full summary text is safe
    final_summary = Truncator(summary_text).chars(MAX_SUMMARY_LENGTH)

    # Log the change
    ActivityLog.objects.create(
        user=request.user,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.id,
        action=final_summary
    )
    print("LOG CREATED:", final_summary)
