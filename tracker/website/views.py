from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddSurveyForm
from .models import survey, design
from django.contrib.contenttypes.models import ContentType
from .models import ActivityLog

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
        # Look Up Survey Details
        survey_record = survey.objects.get(id=pk)
        return render(request, 'survey_detail.html', {'survey_record': survey_record})
    else:
        messages.error(
            request, "You must be logged in to View that page.")
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
    if request.user.is_authenticated:
        current_record = survey.objects.get(id=pk)
        form = AddSurveyForm(request.POST or None, instance=current_record)
        if form.is_valid():
            form.save()
            messages.success(request, "Data Updated Successfully!")
            return redirect('survey')
        return render(request, 'update_survey_record.html', {'form': form})
    else:
        messages.success(request, "You must be logged in to do that.")
        return redirect('home')
