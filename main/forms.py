from django import forms
from .models import Game, SpeedrunType, Speedrun

class SpeedrunForm(forms.ModelForm):
    class Meta:
        model = Speedrun
        fields = ['url', 'time', 'date', 'speedrun_type']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_time(self):
        time = self.cleaned_data.get('time')
        if time is not None and time < 0:
            raise forms.ValidationError("Time cannot be negative!")
        return time