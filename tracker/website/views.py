from openpyxl import Workbook
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddSurveyForm
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


def home(request):
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


def dashboard_design(request):
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
        return render(request, 'dashboard_design.html', {})


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
    old_data = current_record.__dict__.copy()

    form = AddSurveyForm(request.POST or None,
                         instance=current_record, is_update=True)

    if request.method == 'POST' and form.is_valid():
        updated_instance = form.save(commit=False)

        # Define the fields to check for changes
        fields_to_check = ['status', 'responsible',
                           'wo_status', 'tools', 'priority', 'remarks']

        changed_fields = []
        for field in fields_to_check:
            old_value = old_data.get(field)
            new_value = getattr(updated_instance, field)
            # Convert to string to avoid false negatives (especially for User or Choice fields)
            if str(old_value) != str(new_value):
                changed_fields.append(field)

        # Save updated record
        updated_instance.updated_by = request.user
        updated_instance.save()

        # Log changes
        if changed_fields:
            log_changes(request, updated_instance, old_data, changed_fields)

        messages.success(request, "Data Updated Successfully!")
        return redirect('update_survey_record', pk=current_record.id)

    # Fetch logs for this record
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
