from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddSurveyForm
from .models import survey, design
from django.contrib.contenttypes.models import ContentType
from .models import ActivityLog
from .utils.activity_logger import log_changes

# Create your views here.


def home(request):
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
        return render(request, 'home.html', {})


def login_user(request):
    if request.user.is_authenticated:
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
    surveys = survey.objects.all()
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

        # detect changes
        changed_fields = []
        for field in form.changed_data:
            old_value = old_data.get(field)
            new_value = getattr(updated_instance, field)
            if old_value != new_value:
                changed_fields.append(field)

        # save record first
        updated_instance.updated_by = request.user
        updated_instance.save()

        # log the changes using the reusable utility
        if changed_fields:
            log_changes(request, updated_instance, old_data, changed_fields)

        messages.success(request, "Data Updated Successfully!")
        return redirect('update_survey_record', pk=current_record.id)

    # Fetch logs for this record
    logs = ActivityLog.objects.filter(
        content_type=ContentType.objects.get_for_model(survey),
        object_id=current_record.id
    ).order_by('-timestamp')

    return render(request, 'update_survey_record.html',
                  {'form': form, 'record': current_record, 'logs': logs})
