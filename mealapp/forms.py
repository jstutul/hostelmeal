# mealapp/forms.py
from django import forms
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from .models import MealSchedule

# Single form for a MealSchedule row
class MealScheduleForm(forms.ModelForm):
    class Meta:
        model = MealSchedule
        fields = ['noon', 'night', 'guest_noon', 'guest_night']

# FormSet for multiple MealSchedule rows
MealScheduleFormSet = modelformset_factory(
    MealSchedule,
    form=MealScheduleForm,
    extra=0
)

# Optional: Form for adding multiple dates at once
class MealScheduleMultiDateForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())
    start_date = forms.DateField(widget=forms.SelectDateWidget)
    end_date = forms.DateField(widget=forms.SelectDateWidget)
    noon = forms.BooleanField(required=False)
    night = forms.BooleanField(required=False)
    guest_noon = forms.IntegerField(min_value=0, initial=0)
    guest_night = forms.IntegerField(min_value=0, initial=0)

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")
        if start and end and start > end:
            raise forms.ValidationError("End date must be after start date")
        return cleaned_data
