from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import survey


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


SURVEY_STATUS_CHOICES = [
    ('1 - Overlapping Clearance', '1 - Overlapping Clearance'),
    ('2 - Parceling Stage', '2 - Parceling Stage'),
    ('3 - GIS Post', '3 - GIS Post'),
    ('4 - Survey tool Access', '5 - Survey tool Access'),
    ('6 - Survey Stage', '6 - Survey Stage'),
    ('7 - Cluster ID Acquisition', '7 - Cluster ID Acquisition'),
    ('8 - HLD Package Approval', '8 - HLD Package Approval'),
    ('9 - Completed', '9 - Completed'),
]

RESPONSIBLE_CHOICES = [
    ('Hajdyah', 'Hajdyah'),
    ('Mr. Harris', 'Mr. Harris'),
    ('Dawiyat', 'Dawiyat'),
    ('Done', 'Done'),
]

TOOLS_CHOICES = [
    ('1 - PIP Submission', '1 - PIP Submission'),
    ('2 - PIP Approval', '2 - PIP Approval'),
    ('3 - Survey Submission', '3 - Survey Submission'),
    ('4 - Survey Approval', '4 - Survey Approval'),
    ('5 - Completed', '5 - Completed'),
    ('6 - For Cancellation', '6 - For Cancellation'),
    ('7 - Cancelled', '7 - Cancelled'),
]

WO_CHOICES = [
    ('In Progress', 'In Progress'),
    ('Completed', 'Completed'),
    ('Cancelled', 'Cancelled'),
]

PRIORITY_CHOICES = [
    ('Urgent', 'Urgent'),
    ('High', 'High'),
    ('Low', 'Low'),
    ('Done', 'Done'),
]


class AddSurveyForm(forms.ModelForm):
    cluster_name = forms.CharField(required=False, widget=forms.widgets.TextInput(
        attrs={"class": "form-control"}), label="Cluster Name")
    work_order = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={"class": "form-control"}), label="Work Order")
    region = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={"class": "form-control"}), label="Region")
    project_type = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={"class": "form-control"}), label="Project Type")
    RITM = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={"class": "form-control"}), label="RITM")
    target_area = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(
        attrs={"class": "form-control"}), label="Target Area")
    date_assigned = forms.DateField(required=True, widget=forms.widgets.DateInput(
        attrs={"type": "date", "class": "form-control"}), label="Date Assigned")
    status = forms.ChoiceField(
        choices=SURVEY_STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Status",
        initial='1 - Overlapping Clearance'
    )
    responsible = forms.ChoiceField(
        choices=RESPONSIBLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Responsible",
        initial='Hajdyah'
    )
    tools = forms.ChoiceField(
        choices=TOOLS_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Service Now Tools",
        initial='1 - PIP Submission'
    )
    wo_status = forms.ChoiceField(
        choices=WO_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Work Order Status",
        initial='In Progress'
    )
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Priority",
        initial='Low'
    )
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={
            "placeholder": "Remarks",
            "class": "form-control",
            "rows": 4,
            "cols": 50
        }),
        required=False,
        label=""
    )

    class Meta:
        model = survey
        fields = '__all__'
        exclude = ('updated_by',)
