from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView
from django.views.generic import ListView
from django.urls import reverse_lazy
from .forms import RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm, AudioFileForm
from .models import AudioFile, User, PossibleAdmin
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404



class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(to='/')

        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            is_admin = form.cleaned_data.get('is_admin')

            # Check if user is allowed to register as an admin
            if is_admin:
                try:
                    PossibleAdmin.objects.get(first_name=first_name, last_name=last_name)
                except PossibleAdmin.DoesNotExist:
                    messages.error(request, "You cannot register as an admin, please register as a user.")
                    return render(request, self.template_name, {'form': form})

            # Create user and set is_staff
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            user.is_staff = is_admin
            user.save()

            messages.success(request, f'Account created for {username}')
            return redirect(to='login')

        return render(request, self.template_name, {'form': form})


@login_required
def delete_audio(request, audio_id):
    audio = get_object_or_404(AudioFile, pk=audio_id)
    if request.user.is_staff:
        audio.delete()
        return redirect('audio_list')
    else:
        return render(request, 'error.html', {'error_message': 'You do not have permission to delete this audio file.'})


# Class based view that extends from the built in login view to add a remember me functionality
class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('users-home')


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('users-home')


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})



@method_decorator(login_required, name='dispatch')
class AudioFileListView(ListView):
    model = AudioFile
    template_name = 'users/audio_list.html'
    context_object_name = 'audio_files'
    paginate_by = 5 # Change 10 to the number of audio files you want to show per page.

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        audio_files = self.get_queryset()
        paginator = Paginator(audio_files, self.paginate_by)
        page = self.request.GET.get('page')
        audio_files_page = paginator.get_page(page)
        context['audio_files'] = audio_files_page
        print(audio_files)
        return context





@method_decorator(login_required, name='dispatch')
class AudioFileUploadView(FormView):
    form_class = AudioFileForm
    template_name = 'users/audio_upload.html'
    success_url = reverse_lazy('audio_list')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


@login_required
def search_form(request):
    query = request.GET.get('q')
    search_by = request.GET.get('search_by', 'village')  # Default to searching by village

    if query:
        if search_by == 'village':
            audio_files = AudioFile.objects.filter(Village__icontains=query)
        elif search_by == 'description':
            audio_files = AudioFile.objects.filter(description__icontains=query)
        elif search_by == 'uploaded_at':
            audio_files = AudioFile.objects.filter(uploaded_at__icontains=query)
        else:
            audio_files = AudioFile.objects.none()  # Return empty queryset if invalid search_by value is provided
    else:
        audio_files = AudioFile.objects.all()

    return render(request, 'users/search_results.html', {'audio_files': audio_files, 'query': query, 'search_by': search_by})



def home(request):
    return render(request, 'users/home.html')




