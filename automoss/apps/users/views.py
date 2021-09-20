from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as django_login, logout as django_logout, authenticate
from django.views import View
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.http import Http404
from django.conf import settings
from .forms import (
    UserCreationForm,
    LoginForm,
)

class Login(View):
    """ Login view """
    template = "users/auth/login.html"

    def get(self, request):
        """ Get login view """
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return render(request, self.template)

    def post(self, request):
        """ Post login """
        login_form = LoginForm(request=request, data=request.POST)
        # Clean and authenticate login data
        if login_form.is_valid():
            django_login(request, login_form.get_user())
            redirect_url = request.POST.get('next') or settings.LOGIN_REDIRECT_URL
            # Redirect
            if is_safe_url(redirect_url, settings.ALLOWED_HOSTS, require_https=request.is_secure()): 
                return redirect(redirect_url)
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            return render(request, self.template, {"form": login_form})

@method_decorator(login_required, name='dispatch')
class Logout(View):
    """ Logout View """
    template = "users/auth/logged_out.html"

    def get(self, request):
        """ Get logout view """
        django_logout(request)
        return render(request, self.template)

class Register(View):
    """ User registration view """
    template = "users/auth/register.html"
    email_html_template = "users/email/welcome.html"
    email_txt_template = "users/email/welcome.txt"
    email_subject_template = "users/email/subject.txt"
    context = {}

    def get(self, request):
        """ Get registration form """
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        form = UserCreationForm() 
        return render(request, self.template, {**self.context, 'form': form})
    
    def post(self, request):
        """ Post new user information """
        user_form = UserCreationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            django_login(request, user)
            # send account creation confirmation email
            user.send_email( 
                subject_template=self.email_subject_template, 
                body_template=self.email_txt_template, 
                html_template=self.email_html_template, 
                context={ "request" : request },
                broadcast=False
            )
            return redirect(settings.LOGIN_REDIRECT_URL)
        return render(request, self.template, {**self.context, 'form': user_form})
            
    
# @login_required
# def logout(request):
#     """ Logout View : Log user out """
#     if request.method == "GET":
#         django_logout(request)
#         return render(request, "users/logged_out.html")
#     return Http404(f"Logout route with method {request.METHOD}, not found!")
    
    