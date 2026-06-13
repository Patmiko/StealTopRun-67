from django import forms
from django.forms import formset_factory
from django.contrib.admin.widgets import FilteredSelectMultiple
from .models import Category, Game, GameRequest, SpeedrunTypeRequest, UserReport, SpeedrunReport, Speedrun, User
import re


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

class SpeedrunForm(forms.ModelForm):
    time = forms.CharField(
        label="Time (HH:MM:SS:MS)",
        widget=forms.TextInput(attrs={'placeholder': 'HH:MM:SS:MS (e.g., 00:27:39:72).'})
    )

    class Meta:
        model = Speedrun
        fields = ['url', 'time', 'date', 'speedrun_type']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'speedrun_type': forms.HiddenInput(),
        }

    def clean_time(self):
        time_str = self.cleaned_data.get('time', '').strip()
        
        match = re.match(r'^(\d+):(\d+):(\d+):(\d+)$', time_str)
        if not match:
            raise forms.ValidationError("Enter time in a valid format HH:MM:SS:MS (e.g., 00:27:39:72).")
            
        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3))
        
        milliseconds = float(f"0.{match.group(4)}")
        
        if minutes >= 60 or seconds >= 60:
            raise forms.ValidationError("Minutes and seconds must be less than 60.")
        
        total_seconds = (hours * 3600) + (minutes * 60) + seconds + milliseconds
        
        if total_seconds <= 0:
            raise forms.ValidationError("Time must be greater than zero!")
            
        return total_seconds
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
            'name': 'Speedrun Type Name',
        }


class UserReportForm(forms.ModelForm):
    class Meta:
        model = UserReport
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-purple-500 transition shadow-inner'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-purple-500 transition shadow-inner'
            }),
        }


class SpeedrunReportForm(forms.ModelForm):
    class Meta:
        model = SpeedrunReport
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-purple-500 transition shadow-inner'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-purple-500 transition shadow-inner'
            }),
        }

class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-purple-500 transition shadow-inner'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-purple-500 transition shadow-inner'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-purple-600 file:text-white hover:file:bg-purple-700 file:cursor-pointer transition'
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This username is already taken.")
        return username
