from django import forms
from .models import Game, SpeedrunType, Speedrun


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['name', 'release_date', 'img_url']
        # You can add widgets here, e.g., to make release_date a calendar picker
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'}),
        }

class SpeedrunTypeForm(forms.ModelForm):
    class Meta:
        model = SpeedrunType
        fields = ['name', 'game']

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