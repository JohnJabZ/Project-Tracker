from openpyxl import Workbook
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddSurveyForm, AddDesignForm
from .models import survey, design
from django.contrib.contenttypes.models import ContentType
from .models import ActivityLog
from .utils.activity_logger import log_changes
from django.http import HttpResponse
from django.contrib.auth.models import User
import csv
import pandas as pd
import numpy as np


# Create your views here.
# Dashboard Views
def dashboard_design(request):
    # Count all records
    total = design.objects.count()

    # Breakdowns by tools field
    for_submission = design.objects.filter(
        status__icontains="For Submission").count()
    for_survey = design.objects.filter(
        status__icontains="For Survey").count()
    for_approval = design.objects.filter(
        status__icontains="For Approval").count()
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
    overlapping = survey.objects.filter(
        status__icontains="1 - Overlapping Clearance").count()
    parceling = survey.objects.filter(
        status__icontains="2 - Parceling Stage").count()
    gis_post = survey.objects.filter(status__icontains="3 - GIS Post").count()
    tool_access = survey.objects.filter(
        status__icontains="4 - Survey tool Access").count()
    survey_stage = survey.objects.filter(
        status__icontains="5 - Survey Stage").count()
    cluster_id = survey.objects.filter(
        status__icontains="6 - Cluster ID Acquisition").count()
    hld_submission = survey.objects.filter(
        status__icontains="7 - HLD Package Submission").count()
    hld_approval = survey.objects.filter(
        status__icontains="8 - HLD Package Approval").count()
    completed = survey.objects.filter(
        status__icontains="9 - Completed").count()
    for_cancellation = survey.objects.filter(
        status__icontains="10 - For Cancellation").count()
    cancelled = survey.objects.filter(
        status__icontains="11 - Cancelled").count()

    context = {
        "total": total,
        "overlapping": overlapping,
        "parceling": parceling,
        "gis_post": gis_post,
        "tool_access": tool_access,
        "survey_stage": survey_stage,
        "cluster_id": cluster_id,
        "hld_submission": hld_submission,
        "hld_approval": hld_approval,
        "completed": completed,
        "for_cancellation": for_cancellation,
        "cancelled": cancelled,
    }

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
        design_record = design.objects.get(id=pk)

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

    current_record = design.objects.get(id=pk)

    fields_to_check = ['status',
                       'wo_status', 'tools', 'priority', 'remarks']

    old_data = {field: getattr(current_record, field)
                for field in fields_to_check}

    form = AddDesignForm(request.POST or None,
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
        return redirect('update_design_record', pk=current_record.id)

    logs = ActivityLog.objects.filter(
        content_type=ContentType.objects.get_for_model(design),
        object_id=current_record.id
    ).order_by('-timestamp')

    return render(request, 'update_design_record.html', {
        'form': form,
        'record': current_record,
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
                    target_area=row.get("Target Area") or "",
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

            messages.success(request, "Design data imported successfully!")

            if duplicates_skipped:
                messages.warning(
                    request, f"Skipped duplicates: {', '.join(duplicates_skipped)}")

        except Exception as e:
            messages.error(request, f"Error processing file: {e}")

        return redirect("design")
