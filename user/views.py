from django.contrib.auth import update_session_auth_hash
from dashboard.models import Staff
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required  # import added
from django.contrib.auth.views import LogoutView,LoginView
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from user.forms import StaffProfileUpdateForm  
from django.core.mail import send_mail
from .forms import ContactForm
from django.contrib.messages import get_messages
from django.conf import settings

@login_required
def home_redirect(request):
    return redirect('user:login')


@login_required
def profile(request):
    return render(request, 'user/profile.html')

from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import StaffProfileUpdateForm
from dashboard.models import Staff

@login_required
def profile_update(request):
    user = request.user
    staff, _ = Staff.objects.get_or_create(user=user)

    if request.method == "POST":
        form = StaffProfileUpdateForm(request.POST, request.FILES, instance=staff, user=user)

        if form.is_valid():
            # Save form, which handles email and optional password logic
            form.save()

            # Refresh session if password changed
            if form.cleaned_data.get('password'):
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully.")

            # Clear flag on first update
            if staff.must_update_profile:
                staff.must_update_profile = False
                staff.save()

            messages.success(request, "Your profile has been updated successfully!")
            return redirect('user-profile-update')
        else:
            # Form errors handled by Django forms
            messages.error(request, "Please correct the errors below.")

    else:
        form = StaffProfileUpdateForm(instance=staff, user=user)

    return render(request, 'user/profile_update.html', {
        "form": form,
        "staff": staff,
    })


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have been logged out successfully!")
        return super().dispatch(request, *args, **kwargs)
    

class CustomLoginView(LoginView):
    def form_valid(self, form):
        messages.success(self.request, "Login successfully!")
        return super().form_valid(form)
    




def landing_page(request):
    storage = get_messages(request)
    filtered_messages = [m for m in storage if m.tags == 'success']

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            send_mail(
                cd['subject'],
                f"Message from {cd['name']} <{cd['email']}>\n\n{cd['message']}",
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            messages.success(request, "Thank you! We'll get back to you soon.")
            return redirect(reverse('landing_page'))
    else:
        form = ContactForm()

    return render(request, 'landing/home.html', {'form': form, 'messages': filtered_messages})

