from django import forms
from .models import TrainingOpportunity, City, Major


class TrainingOpportunityForm(forms.ModelForm):
    city = forms.ModelChoiceField(
        queryset=City.objects.filter(status=True),
        label="City",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    majors_needed = forms.ModelMultipleChoiceField(
        queryset=Major.objects.all(),
        label="Majors Needed",
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'multiple': 'multiple'})
    )
    start_date = forms.DateField(
        label="Start Date",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    application_deadline = forms.DateField(
        label="Application Deadline",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    requirements = forms.CharField(
        label="Requirements",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    benefits = forms.CharField(
        label="Benefits",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False  # Make benefits optional
    )
    duration = forms.CharField(
        label="Duration",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        label="Status",
        choices=TrainingOpportunity.Status.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, skip_required=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.skip_required = skip_required
        if skip_required:
            for field in self.fields.values():
                field.required = False

    def clean(self):
        cleaned_data = super().clean()
        if not self.skip_required:
            # Additional validation logic if necessary
            pass
        return cleaned_data

    class Meta:
        model = TrainingOpportunity
        fields = [
            'title', 'city', 'majors_needed', 'description', 'requirements',
            'benefits', 'start_date', 'duration', 'application_deadline', 'status'
        ]
