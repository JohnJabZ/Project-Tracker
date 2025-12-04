from openpyxl import Workbook
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from .forms import SignUpForm, AddSurveyForm, AddDesignForm
from django.db.models import Q
from .utils.activity_logger import log_changes
from .models import survey, design, sor, ActivityLog
from tracker.utils.activity_logger import log_changes

import csv
import pandas as pd
import numpy as np


# Create your views here.
# Dashboard Views
def dashboard_design(request):
    # Count all records
    total = design.objects.count()

    # Breakdowns by tools field
    for_survey = design.objects.filter(
        status__icontains="For Survey").count()
    for_submission = design.objects.filter(
        status__icontains="For Submission").count()
    for_approval = design.objects.filter(
        status__icontains="For Approval").count()
    completed = design.objects.filter(
        status__icontains="Completed").count()
    for_cancellation = design.objects.filter(
        status__icontains="For Cancellation").count()
    cancelled = design.objects.filter(
        status__icontains="Cancelled").count()

    context = {
        "total": total,
        "for_submission": for_submission,
        "for_survey": for_survey,
        "for_approval": for_approval,
        "completed": completed,
        "for_cancellation": for_cancellation,
        "cancelled": cancelled,
    }

    return render(request, "dashboard_design.html", context)


def dashboard_asbuilt(request):
    # check to see if logging in
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have logged in!")
            return redirect('home')
        else:
            messages.error(
                request, "Username does not Exist, Please register for an account.")
            return redirect('home')
    else:
        return render(request, 'dashboard_asbuilt.html', {})


def dashboard_sor(request):
    # check to see if logging in
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have logged in!")
            return redirect('home')
        else:
            messages.error(
                request, "Username does not Exist, Please register for an account.")
            return redirect('home')
    else:
        return render(request, 'dashboard_sor.html', {})


def home(request):  # Survey Dashboard
    # Count all records
    total = survey.objects.count()

    # Breakdowns by tools field
    status_counts = {
        "overlapping": survey.objects.filter(status__icontains="1 - Overlapping Clearance").count(),
        "parceling": survey.objects.filter(status__icontains="2 - Parceling Stage").count(),
        "gis_post": survey.objects.filter(status__icontains="3 - GIS Post").count(),
        "tool_access": survey.objects.filter(status__icontains="4 - Survey tool Access").count(),
        "survey_stage": survey.objects.filter(status__icontains="5 - Survey Stage").count(),
        "cluster_id": survey.objects.filter(status__icontains="6 - Cluster ID Acquisition").count(),
        "hld_submission": survey.objects.filter(status__icontains="7 - HLD Package Submission").count(),
        "hld_approval": survey.objects.filter(status__icontains="8 - HLD Package Approval").count(),
        "completed": survey.objects.filter(status__icontains="9 - Completed").count(),
        "for_cancellation": survey.objects.filter(status__icontains="10 - For Cancellation").count(),
        "cancelled": survey.objects.filter(status__icontains="11 - Cancelled").count(),
    }
    context = {"total": total, **status_counts}

    return render(request, "home.html", context)


def login_user(request):
    # check to see if logging in
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You Have Been Logged In!")
            return redirect('home')
        else:
            messages.success(request, "Invalid Username or Password.")

        return redirect('home')

    else:
        return render(request, 'login.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, "You have successfully logged out!")
    return redirect('home')


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()

            # Authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You have registered successfully!")
            return redirect('home')
    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form': form})

    return render(request, 'register.html', {'form': form})


# Survey Views
def survey_list(request):
    surveys = survey.objects.all().order_by('tools')
    # check to see if logging in
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have logged in!")
            return redirect('survey')
        else:
            messages.success(
                request, "Username does not Exist, Please register for an account.")
            return redirect('home')
    else:
        return render(request, 'survey.html', {'surveys': surveys})


def survey_detail(request, pk):
    if request.user.is_authenticated:
        survey_record = survey.objects.get(id=pk)

        # Fetch logs for this specific record
        logs = ActivityLog.objects.filter(
            content_type=ContentType.objects.get_for_model(survey),
            object_id=survey_record.id
        ).order_by('-timestamp')

        return render(request, 'survey_detail.html', {
            'survey_record': survey_record,
            'logs': logs
        })
    else:
        messages.error(request, "You must be logged in to View that page.")
        return redirect('home')


def delete_survey_record(request, pk):
    if request.user.is_authenticated:
        delete_it = survey.objects.get(id=pk)
        delete_it.delete()
        messages.success(request, "Deleted Successfully!")
        return redirect('survey')
    else:
        messages.success(
            request, "You must be logged in to do that.")
        return redirect('home')


def add_survey_record(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to do that.")
        return redirect('home')

    form = AddSurveyForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            survey_instance = form.save(commit=False)
            survey_instance.updated_by = request.user
            survey_instance.save()
            messages.success(request, "Data Added Successfully!")
            return redirect('survey')
        else:
            print(form.errors)  # <-- this will show what’s wrong in the console

    return render(request, 'add_survey_record.html', {'form': form})


def update_survey_record(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to do that.")
        return redirect('home')

    current_record = survey.objects.get(id=pk)

    fields_to_check = ['status',
                       'wo_status', 'tools', 'priority', 'remarks']

    old_data = {field: getattr(current_record, field)
                for field in fields_to_check}

    form = AddSurveyForm(request.POST or None,
                         instance=current_record, is_update=True)

    if request.method == 'POST' and form.is_valid():
        updated_instance = form.save(commit=False)

        changed_fields = [
            field for field in fields_to_check
            if str(old_data[field]) != str(getattr(updated_instance, field))
        ]

        updated_instance.updated_by = request.user
        updated_instance.save()

        if changed_fields:
            log_changes(request, updated_instance, old_data, changed_fields)
        else:
            print("No fields changed")  # Debug only

        messages.success(request, "Data Updated Successfully!")
        return redirect('update_survey_record', pk=current_record.id)

    logs = ActivityLog.objects.filter(
        content_type=ContentType.objects.get_for_model(survey),
        object_id=current_record.id
    ).order_by('-timestamp')

    return render(request, 'update_survey_record.html', {
        'form': form,
        'record': current_record,
        'logs': logs
    })


def export_survey_data(request):
    # Create HTTP response with CSV header
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="survey_export.csv"'},
    )

    writer = csv.writer(response)

    # Write column headers
    writer.writerow([
        "Cluster Name", "Work Order", "Project Type", "Region",
        "RITM", "Target Area", "Assigned Date", "Status", "Responsible",
        "Tools Stage", "Tools WO Status", "Priority", "Remarks",
        "Updated At", "Updated By"
    ])

    # Write row data
    for s in survey.objects.all():
        writer.writerow([
            s.cluster_name,
            s.work_order,
            s.project_type,
            s.region,
            s.RITM,
            s.target_area,
            s.date_assigned,
            s.status,
            s.responsible,
            s.tools,
            s.wo_status,
            s.priority,
            s.remarks,
            s.updated_at,
            s.updated_by.username if s.updated_by else "",
        ])

    return response


def export_survey_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Survey Data"

    ws.append([
        "Cluster Name", "Work Order", "Project Type", "Region",
        "RITM", "Target Area", "Assigned Date", "Status", "Responsible",
        "Tools Stage", "Tools WO Status", "Priority", "Remarks",
        "Updated At", "Updated By"
    ])

    for s in survey.objects.all():
        updated_at_value = s.updated_at

        # Convert timezone-aware datetime to naive
        if updated_at_value and hasattr(updated_at_value, "tzinfo") and updated_at_value.tzinfo:
            updated_at_value = updated_at_value.replace(tzinfo=None)

        ws.append([
            s.cluster_name,
            s.work_order,
            s.project_type,
            s.region,
            s.RITM,
            s.target_area,
            s.date_assigned,
            s.status,
            s.responsible,
            s.tools,
            s.wo_status,
            s.priority,
            s.remarks,
            updated_at_value,
            s.updated_by.username if s.updated_by else "",
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="survey_export.xlsx"'
    wb.save(response)
    return response


def import_survey_view(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            messages.error(request, "No file selected.")
            return redirect("survey")

        try:
            # Detect file type
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            # Remove trailing spaces from headings
            df.columns = [col.strip() for col in df.columns]

            # Replace NaN with None
            df = df.replace({np.nan: None})

            if "Work Order" not in df.columns:
                messages.error(
                    request, "Invalid file: 'Work Order' column missing.")
                return redirect("survey")

            existing_wos = set(
                survey.objects.values_list("work_order", flat=True))
            duplicates_skipped = []

            for _, row in df.iterrows():
                wo = row.get("Work Order")

                if not wo:
                    continue

                wo = str(wo).strip()

                if wo in existing_wos:
                    duplicates_skipped.append(str(wo))
                    continue

                assigned_date = pd.to_datetime(
                    row.get("Assigned Date"), errors="coerce")
                if assigned_date and not pd.isna(assigned_date):
                    assigned_date = assigned_date.date()
                else:
                    assigned_date = None

                updated_by_user = None
                if row.get("Updated By"):
                    updated_by_user = User.objects.filter(
                        username=row["Updated By"]
                    ).first()

                survey.objects.create(
                    cluster_name=row.get("Cluster Name") or "",
                    work_order=wo,
                    project_type=row.get("Project Type") or "",
                    region=row.get("Region") or "",
                    RITM=row.get("RITM") or "",
                    target_area=row.get("Target Area") or "",
                    date_assigned=assigned_date,
                    status=row.get("Status") or "",
                    responsible=row.get("Responsible") or "",
                    tools=row.get("Tools Stage") or "",
                    wo_status=row.get("Tools WO Status") or "",
                    priority=row.get("Priority") or "",
                    remarks=row.get("Remarks") or "",
                    updated_by=updated_by_user,
                    updated_at=row.get("Updated At"),
                )

            messages.success(request, "Survey data imported successfully!")

            if duplicates_skipped:
                messages.warning(
                    request, f"Skipped duplicates: {', '.join(duplicates_skipped)}")

        except Exception as e:
            messages.error(request, f"Error processing file: {e}")

        return redirect("survey")


def survey_filter(request, filter_type):
    """
    Filter surveys by stage based on the filter_type from the dashboard.
    """
    if filter_type == "overlapping":
        items = survey.objects.filter(
            status__icontains="1 - Overlapping Clearance")
        title = "Overlapping Clearance"

    elif filter_type == "parceling":
        items = survey.objects.filter(status__icontains="2 - Parceling Stage")
        title = "Parceling Stage"

    elif filter_type == "gis_post":
        items = survey.objects.filter(status__icontains="3 - GIS Post")
        title = "GIS Post"

    elif filter_type == "tool_access":
        items = survey.objects.filter(
            status__icontains="4 - Survey tool Access")
        title = "Survey Tool Access"

    elif filter_type == "survey_stage":
        items = survey.objects.filter(status__icontains="5 - Survey Stage")
        title = "Survey Stage"

    elif filter_type == "cluster_id":
        items = survey.objects.filter(
            status__icontains="6 - Cluster ID Acquisition")
        title = "Cluster ID Acquisition"

    elif filter_type == "hld_submission":
        items = survey.objects.filter(
            status__icontains="7 - HLD Package Submission")
        title = "HLD Package Submission"

    elif filter_type == "hld_approval":
        items = survey.objects.filter(
            status__icontains="8 - HLD Package Approval")
        title = "HLD Package Approval"

    elif filter_type == "completed":
        items = survey.objects.filter(status__icontains="9 - Completed")
        title = "Completed"

    elif filter_type == "for_cancellation":
        items = survey.objects.filter(
            status__icontains="10 - For Cancellation")
        title = "For Cancellation"

    elif filter_type == "cancelled":
        items = survey.objects.filter(status__icontains="11 - Cancelled")
        title = "Cancelled"

    else:
        items = survey.objects.none()
        title = "Unknown Filter"

    context = {
        "items": items,
        "title": title,
        "count": items.count(),
    }

    return render(request, "survey_filter.html", context)


def survey_search(request):
    qs = survey.objects.all()
    q = request.GET.get("q", "").strip()
    page = int(request.GET.get("page", 1))

    # Column filters
    for key, val in request.GET.items():
        if key.startswith("col_") and val:
            col_index = int(key.split("_")[1])
            # Map column index to model field
            col_map = [
                "cluster_name", "work_order", "project_type", "region",
                "RITM", "target_area", "date_assigned", "status",
                "responsible", "tools", "wo_status", "priority",
                "remarks", "updated_at", "updated_by__username"
            ]
            field = col_map[col_index]
            qs = qs.filter(**{f"{field}__icontains": val})

    if q:
        # global search across multiple fields
        qs = qs.filter(
            cluster_name__icontains=q
        ) | qs.filter(work_order__icontains=q) \
          | qs.filter(project_type__icontains=q) \
          | qs.filter(region__icontains=q)

    paginator = Paginator(qs.order_by("tools"), 50)  # 50 rows per page
    page_obj = paginator.get_page(page)

    rows = []
    for s in page_obj:
        rows.append({
            "html": render_to_string("partials/survey_row.html", {"survey": s})
        })

    return JsonResponse({
        "rows": rows,
        "page": page_obj.number,
        "total_pages": paginator.num_pages,
    })


# Design Views
def design_list(request):
    designs = design.objects.all().order_by('tools')
    # check to see if logging in
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have logged in!")
            return redirect('design')
        else:
            messages.success(
                request, "Username does not Exist, Please register for an account.")
            return redirect('home')
    else:
        return render(request, 'design.html', {'designs': designs})


def design_detail(request, pk):
    if request.user.is_authenticated:
        design_record = get_object_or_404(design, id=pk)

        # Fetch logs for this specific record
        logs = ActivityLog.objects.filter(
            content_type=ContentType.objects.get_for_model(design),
            object_id=design_record.id
        ).order_by('-timestamp')

        return render(request, 'design_detail.html', {
            'design_record': design_record,
            'logs': logs
        })
    else:
        messages.error(request, "You must be logged in to View that page.")
        return redirect('home')


def add_design_record(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to do that.")
        return redirect('home')

    form = AddDesignForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            design_instance = form.save(commit=False)
            design_instance.updated_by = request.user
            design_instance.save()
            messages.success(request, "Data Added Successfully!")
            return redirect('design')
        else:
            print(form.errors)  # <-- this will show what’s wrong in the console

    return render(request, 'add_design_record.html', {'form': form})


def update_design_record(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to do that.")
        return redirect('home')

    current_record = get_object_or_404(design, id=pk)

    # 1. Define the mandatory fields to check for changes
    fields_to_check = ['responsible', 'status',
                       'tools', 'wo_status', 'priority', 'remarks']

    # 2. Collect OLD data as clean, comparable string representations (pre-form submission)
    old_data = {}
    for field in fields_to_check:
        value = getattr(current_record, field)

        if field == 'responsible':
            # FIX: Use a try/except block to safely handle if 'responsible' is a string (CharField)
            # or an object (ForeignKey). The error occurs here on GET request.
            try:
                # If it's a ForeignKey object (User, etc.), get its username or display field
                old_data[field] = value.username if value else 'N/A'
            except AttributeError:
                # If it's a CharField string, just use the string value
                # Use 'N/A' if null/empty
                old_data[field] = str(value) if value else 'N/A'

        elif field == 'remarks':
            # Clean and strip whitespace to ensure "None", "" and " " are treated equally
            old_data[field] = str(value).strip() if value else ''

        else:
            # For other fields, use the simple string value
            old_data[field] = str(value)

    form = AddDesignForm(request.POST or None,
                         instance=current_record, is_update=True)

    if request.method == 'POST' and form.is_valid():
        updated_instance = form.save(commit=False)

        changed_fields = []
        for field in fields_to_check:
            new_value = getattr(updated_instance, field)
            old_value_str = old_data[field]  # The pre-cleaned old value string

            # Determine the comparable string for the NEW value (post-form submission)
            new_value_str = ""
            if field == 'responsible':
                # Reapply the same defensive check for the new value
                try:
                    # If it's a ForeignKey object
                    new_value_str = new_value.username if new_value else 'N/A'
                except AttributeError:
                    # If it's a CharField string
                    new_value_str = str(new_value) if new_value else 'N/A'

            elif field == 'remarks':
                # Get the new instance's cleaned remarks
                new_value_str = str(new_value).strip() if new_value else ''

            else:
                # Get the new instance's simple string value
                new_value_str = str(new_value)

            # Core comparison logic: Check if the clean old value differs from the clean new value
            if old_value_str != new_value_str:
                changed_fields.append(field)

        # 3. Only save and log if changes were actually detected
        if changed_fields:
            updated_instance.updated_by = request.user
            updated_instance.save()

            # Pass the pre-cleaned old_data dictionary to the logger
            log_changes(request, updated_instance, old_data, changed_fields)
        else:
            print("No fields changed.")

        messages.success(request, "Data Updated Successfully!")
        # Use updated_instance.id for the redirect
        return redirect('update_design_record', pk=updated_instance.id)

    logs = ActivityLog.objects.filter(
        content_type=ContentType.objects.get_for_model(design),
        object_id=current_record.id
    ).order_by('-timestamp')

    return render(request, 'update_design_record.html', {
        'form': form,
        'design_record': current_record,
        'logs': logs
    })


def delete_design_record(request, pk):
    if request.user.is_authenticated:
        delete_it = design.objects.get(id=pk)
        delete_it.delete()
        messages.success(request, "Deleted Successfully!")
        return redirect('design')
    else:
        messages.success(
            request, "You must be logged in to do that.")
        return redirect('home')


def design_filter(request, filter_type):
    """
    Filter surveys by stage based on the filter_type from the dashboard.
    """
    if filter_type == "for_survey":
        items = design.objects.filter(
            status__icontains="For Survey")
        title = "For Survey"

    elif filter_type == "for_submission":
        items = design.objects.filter(status__icontains="For Submission")
        title = "For Submission"

    elif filter_type == "for_approval":
        items = design.objects.filter(status__icontains="For Approval")
        title = "For Approval"

    elif filter_type == "completed":
        items = design.objects.filter(status__icontains="Completed")
        title = "Completed"

    elif filter_type == "for_cancellation":
        items = design.objects.filter(
            status__icontains="For Cancellation")
        title = "For Cancellation"

    elif filter_type == "cancelled":
        items = design.objects.filter(status__icontains="Cancelled")
        title = "Cancelled"

    else:
        items = design.objects.none()
        title = "Unknown Filter"

    context = {
        "items": items,
        "title": title,
        "count": items.count(),
    }

    return render(request, "design_filter.html", context)


def export_design_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Survey Data"

    ws.append([
        "District Name", "Cluster Name", "Work Order", "Scope of Work", "SubClass", "Project Type", "Year",
        "RITM #", "Region", "Target Area", "Assigned Date", "Design Type", "Status", "Tools Stage",
        "Tools WO Status", "Responsible", "Priority", "Remarks",
        "Updated At", "Updated By"
    ])

    for s in design.objects.all():
        updated_at_value = s.updated_at

        # Convert timezone-aware datetime to naive
        if updated_at_value and hasattr(updated_at_value, "tzinfo") and updated_at_value.tzinfo:
            updated_at_value = updated_at_value.replace(tzinfo=None)

        ws.append([
            s.district_name,
            s.cluster_name,
            s.work_order,
            s.scope_work,
            s.subclass,
            s.project_type,
            s.year,
            s.RITM,
            s.region,
            s.target_area,
            s.date_assigned,
            s.design_type,
            s.status,
            s.tools,
            s.wo_status,
            s.responsible,
            s.priority,
            s.remarks,
            updated_at_value,
            s.updated_by.username if s.updated_by else "",
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="design_export.xlsx"'
    wb.save(response)
    return response


def export_design_csv(request):
    # Create HTTP response with CSV header
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="design_export.csv"'},
    )

    writer = csv.writer(response)

    # Write column headers
    writer.writerow([
        "District Name", "Cluster Name", "Work Order", "Scope of Work", "SubClass", "Project Type", "Year",
        "RITM #", "Region", "Target Area", "Assigned Date", "Design Type", "Status", "Tools Stage",
        "Tools WO Status", "Responsible", "Priority", "Remarks",
        "Updated At", "Updated By"
    ])

    # Write row data
    for s in design.objects.all():
        writer.writerow([
            s.district_name,
            s.cluster_name,
            s.work_order,
            s.scope_work,
            s.subclass,
            s.project_type,
            s.year,
            s.RITM,
            s.region,
            s.target_area,
            s.date_assigned,
            s.design_type,
            s.status,
            s.tools,
            s.wo_status,
            s.responsible,
            s.priority,
            s.remarks,
            s.updated_at,
            s.updated_by.username if s.updated_by else "",
        ])

    return response


def import_design_view(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            messages.error(request, "No file selected.")
            return redirect("design")

        try:
            # Detect file type
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            # Remove trailing spaces from headings
            df.columns = [col.strip() for col in df.columns]

            # Replace NaN with None
            df = df.replace({np.nan: None})

            if "Work Order" not in df.columns:
                messages.error(
                    request, "Invalid file: 'Work Order' column missing.")
                return redirect("design")

            existing_wos = set(
                design.objects.values_list("work_order", flat=True))
            duplicates_skipped = []

            for index, row in df.iterrows():
                try:
                    wo = str(row.get("Work Order")).strip()
                    if not wo or wo in existing_wos:
                        duplicates_skipped.append(wo)
                        continue

                    assigned_date = pd.to_datetime(
                        row.get("Assigned Date"), errors="coerce")
                    if assigned_date and not pd.isna(assigned_date):
                        assigned_date = assigned_date.date()
                    else:
                        assigned_date = None

                    updated_by_user = None
                    if row.get("Updated By"):
                        updated_by_user = User.objects.filter(
                            username=row["Updated By"]).first()

                    # Convert Target Area properly
                    raw_target = row.get("Target Area")
                    if pd.isna(raw_target) or str(raw_target).strip() == "":
                        target_area = None
                    else:
                        try:
                            target_area = int(float(raw_target))  # If numeric
                        except:
                            # fallback to string
                            target_area = str(raw_target).strip()

                    design.objects.create(
                        district_name=row.get("District Name") or "",
                        cluster_name=row.get("Cluster Name") or "",
                        work_order=wo,
                        scope_work=row.get("Scope of Work") or "",
                        subclass=row.get("SubClass") or "",
                        project_type=row.get("Project Type") or "",
                        year=row.get("Year") or "",
                        RITM=row.get("RITM #") or "",
                        region=row.get("Region") or "",
                        target_area=target_area,
                        date_assigned=assigned_date,
                        design_type=row.get("Design Type") or "",
                        status=row.get("Status") or "",
                        tools=row.get("Tools Stage") or "",
                        wo_status=row.get("Tools WO Status") or "",
                        responsible=row.get("Responsible") or "",
                        priority=row.get("Priority") or "",
                        remarks=row.get("Remarks") or "",
                        updated_by=updated_by_user,
                        updated_at=row.get("Updated At"),
                    )
                except Exception as e:
                    print(
                        f"Error on row {index+1}: {e}, Work Order: {row.get('Work Order')}, Target Area: {row.get('Target Area')}")

            messages.success(request, "Design data imported successfully!")

            if duplicates_skipped:
                messages.warning(
                    request, f"Skipped duplicates: {', '.join(duplicates_skipped)}")

        except Exception as e:
            messages.error(request, f"Error processing file: {e}")

        return redirect("design")


def get_page_range(current_page, total_pages, window):
    # Calculate the start and end of the page range
    start = max(1, current_page - window)
    end = min(total_pages, current_page + window)

    # Adjust range bounds if the range is near the start or end
    # This ensures a fixed number of links when possible.
    if current_page - window < 1:
        end = min(total_pages, end + (window - current_page + 1))
    if current_page + window > total_pages:
        start = max(1, start - (current_page + window - total_pages))

    return range(start, end + 1)


def design_search(request):
    # 1. Get Parameters
    global_query = request.GET.get('q', '').strip()
    page = int(request.GET.get('page', 1))

    # --- CRITICAL: Mapping Column Index to Model Field Name ---
    # This must match the <input data-col="X"> in design.html and the field in models.py
    COLUMN_FIELD_MAP = {
        0: 'district_name',
        1: 'cluster_name',
        2: 'work_order',
        3: 'scope_work',
        4: 'subclass',
        5: 'project_type',
        6: 'year',
        7: 'RITM',
        8: 'region',
        9: 'target_area',
        10: 'date_assigned',
        11: 'design_type',
        12: 'status',
        13: 'tools',        # 'Stage' in HTML maps to 'tools' in model/row
        14: 'wo_status',    # 'WO' in HTML maps to 'wo_status' in model/row
        15: 'responsible',
        16: 'priority',
        17: 'remarks',
        18: 'updated_at',
        19: 'updated_by__username',  # Use __username for FK field
    }

    # Start with all objects
    designs_queryset = design.objects.all().select_related('updated_by')

    # 2. Apply Global Search (searchInput: 'q' parameter) - Search ALL TEXT fields
    if global_query:
        # Create an OR condition across all relevant text/char fields
        q_objects = Q()
        searchable_fields = [
            'district_name', 'cluster_name', 'work_order', 'scope_work',
            'subclass', 'project_type', 'RITM', 'region', 'design_type',
            'status', 'tools', 'wo_status', 'responsible', 'priority',
            'remarks', 'updated_by__username'  # Search by updated_by's username
        ]

        for field in searchable_fields:
            # Use __icontains for case-insensitive partial match
            q_objects |= Q(**{f'{field}__icontains': global_query})

        designs_queryset = designs_queryset.filter(q_objects)

    # 3. Apply Column Filters (column-filter: 'col_X' parameters) - Search SPECIFIC fields
    for key, value in request.GET.items():
        if key.startswith('col_') and value.strip():
            try:
                col_index = int(key.split('_')[1])
                field_name = COLUMN_FIELD_MAP.get(col_index)
                filter_value = value.strip()

                if field_name:
                    # Special handling for Foreign Key (updated_by)
                    if field_name == 'updated_by__username':
                        designs_queryset = designs_queryset.filter(
                            updated_by__username__icontains=filter_value)

                    # Special handling for Integer/Date fields (year, target_area, date_assigned)
                    elif field_name in ['year', 'target_area']:
                        # Attempt exact match for numbers, ignore if not a valid number
                        try:
                            designs_queryset = designs_queryset.filter(
                                **{f'{field_name}': int(filter_value)})
                        except ValueError:
                            # If not a valid number, skip filter for this column
                            continue

                    elif field_name in ['date_assigned', 'updated_at']:
                        # For dates, an icontains search might match year/month, or a full date filter is complex
                        # We'll use __icontains on the string representation for simple searching
                        designs_queryset = designs_queryset.filter(
                            **{f'{field_name}__icontains': filter_value})

                    # Default: Apply __icontains for all other text/char fields
                    else:
                        designs_queryset = designs_queryset.filter(
                            **{f'{field_name}__icontains': filter_value})

            except (ValueError, IndexError):
                # Ignore invalid column keys
                continue

    # 4. Pagination
    PAGINATION_SIZE = 10
    PAGE_WINDOW = 2  # Define the window size for pagination
    paginator = Paginator(designs_queryset, PAGINATION_SIZE)
    page_obj = paginator.get_page(page)

    # Calculate smart page range to send to client
    page_numbers = list(get_page_range(
        page_obj.number, paginator.num_pages, PAGE_WINDOW))

    # 5. Prepare JSON Response
    data = {
        "rows": [{"html": render_to_string("_design_row.html", {"design": design})} for design in page_obj],
        "page": page_obj.number,
        "total_pages": paginator.num_pages,
        # Send the calculated page numbers to the client
        "page_numbers": page_numbers,
        # Add next/previous existence for convenience
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None,
        "previous_page_number": page_obj.previous_page_number() if page_obj.has_previous() else None,
    }
    return JsonResponse(data)


# SOR Views
def sor_list(request):
    sors = sor.objects.all().order_by('tools')
    # check to see if logging in
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have logged in!")
            return redirect('design')
        else:
            messages.success(
                request, "Username does not Exist, Please register for an account.")
            return redirect('home')
    else:
        return render(request, 'design.html', {'designs': sors})
