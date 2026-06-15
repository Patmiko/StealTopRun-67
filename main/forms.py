from django import forms
from django.forms import formset_factory
from django.contrib.admin.widgets import FilteredSelectMultiple
from .models import Category, Game, GameRequest, SpeedrunTypeRequest, UserReport, SpeedrunReport, Speedrun, User, SpeedrunType
import re


class ResolveSpeedrunReportForm(forms.Form):
    request_id = forms.IntegerField(widget=forms.HiddenInput())
    
    reject = forms.BooleanField(required=False, label="Dismiss Report")
    ban_user = forms.BooleanField(required=False, label="Ban User and Delete Run")
    delete_run = forms.BooleanField(required=False, label="Delete Run Only")

    def clean(self):
        cleaned_data = super().clean()
        reject = cleaned_data.get('reject')
        ban = cleaned_data.get('ban_user')
        delete = cleaned_data.get('delete_run')

        selected_count = sum([bool(reject), bool(ban), bool(delete)])
        
        if selected_count > 1:
            raise forms.ValidationError("Please select only one action (Dismiss, Ban User, or Delete Run).")
            
        return cleaned_data

ResolveSpeedrunReportFormSet = formset_factory(ResolveSpeedrunReportForm, extra=0)

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
                'class': 'w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-purple-500 transition shadow-inner',
                'minlength': '3',
                'maxlength': '20',
                'pattern': '^[a-zA-Z0-9_]+$',
                'title': '3-20 characters, letters, numbers, and underscores only.'
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
        
        if not (3 <= len(username) <= 20) or not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise forms.ValidationError('Username must be 3-20 characters long and contain only letters, numbers, and underscores.')
        
        if User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This username is already taken.')
            
        return username

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

class AcceptSpeedrunRequestForm(forms.Form):
    request_id = forms.IntegerField(widget=forms.HiddenInput())
    url = forms.CharField(max_length=255, required=False)
    time = forms.FloatField(required=False)
    
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
    speedrun_type = forms.ModelChoiceField(
        queryset=SpeedrunType.objects.all(), 
        required=False,
        widget=forms.Select()
    )
    reject = forms.BooleanField(required=False, initial=False)

    def clean(self):
        cleaned_data = super().clean()
        reject = cleaned_data.get('reject')
        
        if not reject:
            if not cleaned_data.get('url'):
                self.add_error('url', 'This field is required when accepting.')
            if not cleaned_data.get('time'):
                self.add_error('time', 'This field is required when accepting.')
            if not cleaned_data.get('date'):
                self.add_error('date', 'This field is required when accepting.')
            if not cleaned_data.get('speedrun_type'):
                self.add_error('speedrun_type', 'This field is required when accepting.')
        return cleaned_data

AcceptSpeedrunRequestFormSet = forms.formset_factory(AcceptSpeedrunRequestForm, extra=0)

class ResendVerificationForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition',
            'minlength': '8'
        }),
        min_length=8
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition',
            'minlength': '8'
        }),
        min_length=8,
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition',
                'minlength': '3',
                'maxlength': '20',
                'pattern': '^[a-zA-Z0-9_]+$',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition',
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not (3 <= len(username) <= 20) or not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise forms.ValidationError('Username must be 3-20 characters long and contain only letters, numbers, and underscores.')
        
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Passwords do not match.')
            
        return cleaned_data