import pandas as pd
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from website.models import design


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
    help = "Import survey data from CSV or Excel and skip duplicate work orders in the database"

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

        # Normalize work order values
        if "Work Order" not in df.columns:
            self.stdout.write(self.style.ERROR(
                "ERROR: 'Work Order' column is missing"))
            return

        df["Work Order"] = df["Work Order"].astype(str).str.strip()

        # Get existing work orders from DB once
        existing_wos = set(
            design.objects.values_list("work_order", flat=True)
        )

        # Track duplicates found in DB
        duplicates_skipped = []

        # Process each row
        for _, row in df.iterrows():

            wo = clean_value(row.get("Work Order"))

            # Skip if work order already exists in DB
            if wo in existing_wos:
                duplicates_skipped.append(wo)
                continue

            assigned_date = parse_date(row.get("Assigned Date"))
            if assigned_date is None:
                continue  # Mandatory field missing, skip row

            updated_by_user = None
            if pd.notna(row.get("Updated By", None)):
                updated_by_user = User.objects.filter(
                    username=row["Updated By"]
                ).first()

            design.objects.create(
                district_name=clean_value(row.get("District Name")),
                cluster_name=clean_value(row.get("Cluster Name")),
                work_order=wo,
                scope_work=clean_value(row.get("Scope of Work")),
                subclass=clean_value(row.get("SubClass")),
                project_type=clean_value(row.get("Project Type")),
                year=clean_value(row.get("Year")),
                RITM=clean_value(row.get("RITM #")),
                region=clean_value(row.get("Region")),
                target_area=row.get("Target Area") if pd.notna(
                    row.get("Target Area")) else None,
                date_assigned=assigned_date,
                design_type=clean_value(row.get("Design Type")),
                status=clean_value(row.get("Status")),
                tools=clean_value(row.get("Tools Stage")),
                wo_status=clean_value(row.get("Tools WO Status")),
                responsible=clean_value(row.get("Responsible")),
                priority=clean_value(row.get("Priority")),
                remarks=clean_value(row.get("Remarks")),
                updated_by=updated_by_user,
                updated_at=parse_date(row.get("Updated At")),

            )

        # Final success message
        self.stdout.write(self.style.SUCCESS(
            "Design data imported successfully!"))

        # Inform user about excluded duplicates
        if duplicates_skipped:
            duplicates_str = ", ".join(duplicates_skipped)
            self.stdout.write(
                self.style.WARNING(
                    f"Duplicate work orders found and excluded: {duplicates_str}"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("No duplicate work orders found.")

            )
