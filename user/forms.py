from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()
from dashboard.models import Staff

#Your view for editing a staff must instantiate
class StaffProfileUpdateForm(forms.ModelForm):
    # Editable fields from related User model
    first_name = forms.CharField(required=True, label="First Name")
    last_name = forms.CharField(required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email Address")
    password = forms.CharField(
        widget=forms.PasswordInput, required=False, label="New Password"
    )
    old_password = forms.CharField(
        widget=forms.PasswordInput, required=False, label="Old Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput, required=False, label="Confirm New Password"
    )

    class Meta:
        model = Staff
        fields = ['phone', 'address', 'profile_picture']  # Staff fields only
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': 'Enter phone number'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter address'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')  # Expect user instance on form init
        super().__init__(*args, **kwargs)

        # Prefill email from the user instance
        self.fields['first_name'].initial = self.user.first_name
        self.fields['last_name'].initial = self.user.last_name
        self.fields['email'].initial = self.user.email

        # You can disable fields here if needed, e.g. role or join_date if added
        if 'role' in self.fields:
            self.fields['role'].disabled = True
        if 'join_date' in self.fields:
            self.fields['join_date'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        old_password = cleaned_data.get('old_password')


        if password or confirm_password:
         if not old_password:
            raise forms.ValidationError("You must enter your old password to change to a new one.")
         if not self.user.check_password(old_password):
            raise forms.ValidationError("Old password is incorrect.")
         if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
         if password and len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")

        return cleaned_data

    def save(self, commit=True):
        # Save Staff fields first
        staff = super().save(commit=False)

        # Update the related User fields
        self.user.first_name = self.cleaned_data.get('first_name')
        self.user.last_name = self.cleaned_data.get('last_name')
        self.user.email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if password:
            self.user.set_password(password)

        if commit:
            self.user.save()
            staff.user = self.user  # Ensure the relationship is intact
            staff.save()

        return staff


# view for adding a staff


class StaffCreateForm(forms.ModelForm):
    # User-related fields
    username = forms.CharField(required=True, label="Username")
    first_name = forms.CharField(required=True, label="First Name")
    last_name = forms.CharField(required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Initial Password")

    # Role is for the User model, not Staff
    ROLE_CHOICES = User.ROLE_CHOICES
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = Staff
        fields = ['phone', 'address', 'profile_picture']

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)  # Pass in from view
        if not self.company:
            raise ValueError("Company must be provided to the form")
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.Use Another Username ")
        return username

    def save(self, commit=True):
        # Create the User
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            role=self.cleaned_data['role'],
            company=self.company,
        )
        
           # The signal will create Staff automatically
        staff = user.staff  # get the created Staff instance

    # Update extra Staff fields
        staff.phone = self.cleaned_data.get('phone')
        staff.address = self.cleaned_data.get('address')
        
        if self.cleaned_data.get('profile_picture'):
          staff.profile_picture = self.cleaned_data.get('profile_picture')

        if commit:
          staff.save()

        return staff



class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Your name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'you@example.com'
    }))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Subject'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control', 'rows': 5, 'placeholder': 'Type your message here...'
    }))
