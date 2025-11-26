import pandas as pd
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from website.models import survey


def clean_value(value):
    """Return empty string instead of NaN or None."""
    return "" if pd.isna(value) else value


def parse_date(value):
    if pd.isna(value) or value == "":
        return None
    try:
        return pd.to_datetime(value).date()
    except:
        return None


class Command(BaseCommand):
    help = "Import survey data from CSV or Excel"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]

        # Load data
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        df.columns = [col.strip() for col in df.columns]

        for _, row in df.iterrows():

            assigned_date = parse_date(row.get("Assigned Date"))

            if assigned_date is None:
                continue  # skip rows missing mandatory date

            updated_by_user = None
            if pd.notna(row.get("Updated By", None)):
                updated_by_user = User.objects.filter(
                    username=row["Updated By"]
                ).first()

            survey.objects.create(
                cluster_name=clean_value(row.get("Cluster Name")),
                work_order=clean_value(row.get("Work Order")),
                project_type=clean_value(row.get("Project Type")),
                region=clean_value(row.get("Region")),
                RITM=clean_value(row.get("RITM")),
                target_area=row.get("Target Area") if pd.notna(
                    row.get("Target Area")) else None,
                date_assigned=assigned_date,
                status=clean_value(row.get("Status")),
                responsible=clean_value(row.get("Responsible")),
                tools=clean_value(row.get("Tools Stage")),
                wo_status=clean_value(row.get("Tools WO Status")),
                priority=clean_value(row.get("Priority")),
                remarks=clean_value(row.get("Remarks")),
                updated_by=updated_by_user,
                updated_at=parse_date(row.get("Updated At")),
            )

        self.stdout.write(self.style.SUCCESS(
            "Survey data imported successfully!"))
