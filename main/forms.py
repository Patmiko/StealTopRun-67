from django import forms
from django.forms import formset_factory
from django.contrib.admin.widgets import FilteredSelectMultiple
from .models import Category, Game, GameRequest, SpeedrunTypeRequest, UserReport, SpeedrunReport


class AcceptGameRequestForm(forms.Form):
    request_id = forms.IntegerField(widget=forms.HiddenInput())
    
    reject = forms.BooleanField(
        required=False, 
        label="Reject this request completely",
        widget=forms.CheckboxInput(attrs={'class': 'reject-checkbox'})
    )
    
    game_title = forms.CharField(
        required=False, 
        label="Final Game Title",
        widget=forms.TextInput(attrs={'class': 'vTextField', 'style': 'font-weight: bold;'})
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4, 
            'placeholder': 'Enter game description...',
            'class': 'vLargeTextField'
        }), 
        required=False
    )
    
    cover_image = forms.ImageField(label="Cover Image", required=False)
    
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=FilteredSelectMultiple("Categories", is_stacked=False), 
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        is_rejected = cleaned_data.get('reject')
        
        if not is_rejected:
            if not cleaned_data.get('game_title'):
                self.add_error('game_title', 'A final game title is required to accept this request.')
            if not cleaned_data.get('description'):
                self.add_error('description', 'A description is required to accept this request.')
            if not cleaned_data.get('cover_image'):
                self.add_error('cover_image', 'A cover image is required to accept this request.')
            if not cleaned_data.get('categories'):
                self.add_error('categories', 'You must select at least one category to accept this request.')
                
        return cleaned_data

AcceptGameRequestFormSet = formset_factory(AcceptGameRequestForm, extra=0)


class AcceptSpeedrunTypeRequestForm(forms.Form):
    request_id = forms.IntegerField(widget=forms.HiddenInput())
    
    # Checkbox for rejection
    reject = forms.BooleanField(
        required=False, 
        label="Reject this speedrun type request completely",
        widget=forms.CheckboxInput(attrs={'class': 'reject-checkbox'})
    )
    
    name = forms.CharField(
        required=False, 
        label="Final Speedrun Type Name",
        widget=forms.TextInput(attrs={'class': 'vTextField', 'style': 'font-weight: bold;'})
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4, 
            'placeholder': 'Enter type description or rules...',
            'class': 'vLargeTextField'
        }), 
        required=False
    )
    
    game = forms.ModelChoiceField(
        queryset=Game.objects.all(),
        label="Assigned Game",
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        is_rejected = cleaned_data.get('reject')
        
        if not is_rejected:
            if not cleaned_data.get('name'):
                self.add_error('name', 'A final name is required to accept this request.')
            if not cleaned_data.get('description'):
                self.add_error('description', 'A description is required to accept this request.')
            if not cleaned_data.get('game'):
                self.add_error('game', 'You must assign this speedrun type to a game.')
                
        return cleaned_data

AcceptSpeedrunTypeRequestFormSet = formset_factory(AcceptSpeedrunTypeRequestForm, extra=0)
from .models import Speedrun

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

class GameRequestForm(forms.ModelForm):
    class Meta:
        model = GameRequest
        fields = ['title', 'description', 'release_date']
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'}),
        }

class SpeedrunTypeRequestForm(forms.ModelForm):
    class Meta:
        model = SpeedrunTypeRequest
        fields = ['game', 'name', 'description']
        labels = {
            'name': 'Category Name',
        }


class UserReportForm(forms.ModelForm):
    class Meta:
        model = UserReport
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class SpeedrunReportForm(forms.ModelForm):
    class Meta:
        model = SpeedrunReport
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }