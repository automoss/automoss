from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import (
    login as django_login,
    logout as django_logout,
    update_session_auth_hash,
)
from django.views import View
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.http import (
    JsonResponse,
    HttpResponseNotFound,
)
from django.conf import settings
from .forms import (
    UserCreationForm,
    LoginForm,
    PasswordForgottenForm,
    PasswordResetForm,
    PasswordUpdateForm,
    EmailForm,
    UnverifiedError
)
from .tokens import (
    email_confirmation_token,
    confirm_registration_token,
    password_reset_token,
)
from .models import (
    User,
    Email
)


class Login(View):
    """ Login view """

    template = "users/auth/login.html"
    email_html_template = "users/email/welcome.html"
    email_txt_template = "users/email/welcome.txt"
    email_subject_template = "users/email/welcome-subject.txt"

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
            redirect_url = request.POST.get(
                'next') or settings.LOGIN_REDIRECT_URL
            # Redirect
            if is_safe_url(redirect_url, settings.ALLOWED_HOSTS, require_https=request.is_secure()):
                return redirect(redirect_url)
            return redirect(settings.LOGIN_REDIRECT_URL)

        else:
            # if user login failed because not yet verified
            if isinstance(login_form.errors.as_data().get('__all__')[0], UnverifiedError):
                # send account creation confirmation email
                login_form.get_user().send_email(
                    subject_template=self.email_subject_template,
                    body_template=self.email_txt_template,
                    html_template=self.email_html_template,
                    context={
                        "request": request,
                        "user": login_form.get_user(),
                        "token": confirm_registration_token.make_token(login_form.get_user())
                    },
                    broadcast=False
                )
            return render(request, self.template, {"form": login_form})


@method_decorator(login_required, name='dispatch')
class Logout(View):
    """ Logout View """

    template = "users/auth/logged_out.html"

    def get(self, request):
        """ Get logout view """
        django_logout(request)
        return render(request, self.template)


@method_decorator(login_required, name='dispatch')
class Profile(View):
    """ Profile View """

    template = "users/profile/profile.html"
    email_html_template = "users/email/confirm-email.html"
    email_txt_template = "users/email/confirm-email.txt"
    email_subject_template = "users/email/confirm-email-subject.txt"

    def get(self, request):
        """ Get profile view """
        return render(request, self.template, {
            'mailing_list': request.user.email_set.all(),
            'user': request.user
        })

    def post(self, request):
        """ Post new profile data """
        form_type = request.POST.get('form')

        # Password change
        if form_type == 'password-change':
            change_password_form = PasswordUpdateForm(
                request.user, request.POST)
            if change_password_form.is_valid():
                # Save and update session auth hash (logs out all other user instances except current)
                change_password_form.save()
                update_session_auth_hash(
                    self.request, change_password_form.user)
            return render(request, self.template, {
                'passwordform': change_password_form,
                'mailing_list': request.user.email_set.all(),
                'user': request.user
            })

        # Mailing List change
        elif form_type == 'mail-list-change':
            clean_emails = []
            for email in request.POST.get('emails').split(","):
                email_form = EmailForm(
                    {"user": request.user, "email_address": email})
                # Save if valid
                if email_form.is_valid():
                    result = email_form.save()
                    # Send verification email if new email
                    if result:
                        result.send_email(
                            subject_template=self.email_subject_template,
                            body_template=self.email_txt_template,
                            html_template=self.email_html_template,
                            context={
                                "request": request,
                                "user": request.user,
                                "email": result,
                                "token": email_confirmation_token.make_token(result)
                            }
                        )
                clean_emails.append(
                    email_form.cleaned_data.get("email_address"))
            # Remove emails not listed in the post request
            deleted_emails = request.user.email_set.all().exclude(
                email_address__in=clean_emails)
            deleted_emails.delete()
            return JsonResponse({"emails" : [(str(email), email.is_verified) for email in request.user.email_set.all()]})
        else:
            # Invalid post request
            return HttpResponseNotFound()


class Register(View):
    """ User registration view """

    template = "users/auth/register.html"
    confirm_template = "users/auth/confirm.html"
    email_html_template = "users/email/welcome.html"
    email_txt_template = "users/email/welcome.txt"
    email_subject_template = "users/email/welcome-subject.txt"
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
            # send account creation confirmation email
            user.send_email(
                subject_template=self.email_subject_template,
                body_template=self.email_txt_template,
                html_template=self.email_html_template,
                context={
                    "request": request,
                    "user": user,
                    "token": confirm_registration_token.make_token(user)
                },
                broadcast=False
            )
            return render(request, self.confirm_template,
                          {
                              "message": "Check your email inbox for a verification link.",
                              "header": "Verify Your Account",
                              "action": "Go to Login"
                          })
        return render(request, self.template, {**self.context, 'form': user_form})


class ForgotPassword(View):
    """ View for forgotten passwords """

    template = "users/auth/forgot-password.html"
    email_html_template = "users/email/forgot-password.html"
    email_txt_template = "users/email/forgot-password.txt"
    email_subject_template = "users/email/forgot-password-subject.txt"

    def get(self, request):
        """ Get form for entering course code to reset password """
        forgot_password_form = PasswordForgottenForm()
        return render(request, self.template, context={"form": forgot_password_form})

    def post(self, request):
        """ Request change of password for course account """
        forgot_password_form = PasswordForgottenForm(request.POST)
        user = None
        if forgot_password_form.is_valid():
            user = forgot_password_form.get_user()
            if user is not None:
                # send account creation confirmation email
                user.send_email(
                    subject_template=self.email_subject_template,
                    body_template=self.email_txt_template,
                    html_template=self.email_html_template,
                    context={
                        "request": request,
                        "user": user,
                        "token": password_reset_token.make_token(user)
                    },
                    broadcast=False
                )
        return render(request, self.template, context={"form": forgot_password_form, "feedback": True})


class ResetPassword(View):
    """ View for resetting passwords """
    template = "users/auth/reset-password.html"
    info_template = "users/auth/confirm.html"

    def get(self, request, uid, token):
        """ Get form for entering new password """
        try:
            user = User.objects.get(user_id=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and password_reset_token.check_token(user, token):
            # Return password reset form
            password_reset_form = PasswordResetForm(user)
            return render(request, self.template,
                          {
                              "form": password_reset_form,
                              "uid": uid,
                              "token": token,
                          })
        else:
            # Invalid verification link
            return render(request, self.info_template,
                          {
                              "message": "That reset link is either invalid or has expired.\nTo generate a new one, go to 'Forgot Password' and re-enter your course code",
                              "header": "Invalid Password Reset Link",
                              "action": "Go to Login"
                          })

    def post(self, request, uid, token):
        """ Update password """
        try:
            user = User.objects.get(user_id=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and password_reset_token.check_token(user, token):
            # Create password reset form
            password_reset_form = PasswordResetForm(user, request.POST)
            if password_reset_form.is_valid():
                # Update password if valid
                password_reset_form.save()
                # Return confirmation
                return render(request, self.info_template,
                              {
                                  "message": "Your password was successfully changed!",
                                  "header": "Password Updated",
                                  "action": "Go to Login"
                              })
            else:
                return render(request, self.template,
                              {
                                  "form": password_reset_form,
                                  "uid": uid,
                                  "token": token,
                              })
        else:
            # Invalid verification link
            return render(request, self.info_template,
                          {
                              "message": "That reset link is either invalid or has expired.\nTo generate a new one, go to 'Forgot Password' and re-enter your course code.",
                              "header": "Invalid Password Reset Link",
                              "action": "Go to Login"
                          })


class Confirm(View):
    """ View for confirming account """

    template = "users/auth/confirm.html"

    def get(self, request, uid, token):
        """ Attempt to verify user """
        try:
            user = User.objects.get(user_id=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and confirm_registration_token.check_token(user, token):
            # Verify user
            user.is_verified = True
            user.save()
            return render(request, self.template,
                          {
                              "message": "Your account has been successfully verified! You may now login to your account.",
                              "header": "Account Verified",
                              "action": "Login to your Account"
                          })
        else:
            # Invalid verification link
            return render(request, self.template,
                          {
                              "message": "That verification link is either invalid or has expired.\nTo generate a new one, enter your account credentials on the login page.\n An email containing a new link will be sent to you.",
                              "header": "Invalid Verification Link",
                              "action": "Go to Login"
                          })


class ConfirmEmail(View):
    """ View for confirming email """

    template = "users/auth/confirm.html"

    def get(self, request, eid, token):
        """ Attempt to verify email """
        try:
            email = Email.objects.get(email_id=eid)
        except(TypeError, ValueError, OverflowError, Email.DoesNotExist):
            email = None
        if email is not None and email_confirmation_token.check_token(email, token):
            # Verify user
            email.is_verified = True
            email.save()
            return render(request, self.template,
                          {
                              "message": "Your email has been successfully verified! You can now receive notifications.",
                              "header": "Email Verified",
                              "action": "Go to Login"
                          })
        else:
            # Invalid verification link
            return render(request, self.template,
                          {
                              "message": "That verification link is either invalid or has expired.\nAsk the account holder to generate a new one.",
                              "header": "Invalid Verification Link",
                              "action": "Go to Login"
                          })
