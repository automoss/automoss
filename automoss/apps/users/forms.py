import unicodedata
from .models import (
    User,
    Email
)
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    SetPasswordForm,
    PasswordChangeForm,
)
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from ..moss.moss import MOSS
from django.contrib.auth.validators import UnicodeUsernameValidator


class UsernameField(forms.CharField):
    """ User name field - based on Django's UsernameField """

    def to_python(self, value):
        return unicodedata.normalize('NFKC', super().to_python(value))

    def widget_attrs(self, widget):
        return {
            **super().widget_attrs(widget),
            'autocapitalize': 'none',
            'autocomplete': 'username',
        }


class UserCreationForm(forms.ModelForm):
    """ User registration form - based on Django's UserCreationForm """
    error_messages = {
        'password_mismatch': 'The two password fields didn’t match.',
        'invalid_moss_id': 'The MOSS ID provided is not valid.',
        'moss_error': 'MOSS could not verify your ID at this time. Please try again later.'
    }
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text="Enter a password.",
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text="Re-enter your password.",
    )

    class Meta:
        model = User
        fields = (
            'course_code',
            'primary_email_address',
            'moss_id',
        )
        field_classes = {'course_code': UsernameField}

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password2', error)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def clean_moss_id(self):
        clean_moss_id = self.cleaned_data.get('moss_id')
        valid_id = False
        try:
            valid_id = MOSS.validate_moss_id(
                clean_moss_id, raise_if_connection_error=True)
        except ConnectionError:
            raise ValidationError(
                self.error_messages['moss_error'],
                code='could_not_verify',
            )
        if valid_id:
            return clean_moss_id
        raise ValidationError(
            self.error_messages['invalid_moss_id'],
            code='invalid_moss_id',
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UnverifiedError(ValidationError):
    """ Represents an unverified user """


class LoginForm(AuthenticationForm):
    """ User login form """
    error_messages = {
        'invalid_login': 'The course code and password entered were incorrect.',
        'inactive': 'That account is diabled.',
        'unverified': "Please verify your account. An email has been sent to your inbox."
    }

    def confirm_login_allowed(self, user):
        """ Determines whether a user is allowed to login """
        if not user.is_active:
            raise ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )
        if not user.is_verified:
            raise UnverifiedError(
                self.error_messages['unverified'],
                code='unverified',
            )


class PasswordForgottenForm(forms.Form):
    """ Form for resetting forgotten password """

    course_code_validator = UnicodeUsernameValidator()

    # Course code
    course_code = forms.CharField(
        max_length=150,
        validators=[course_code_validator]
    )

    def get_user(self):
        """Given a course code, return matching user who should receive a reset email.
        """
        try:
            user = User._default_manager.get(**{
                'course_code': self.cleaned_data['course_code'],
                'is_active': True,
            })
            return user
        except User.DoesNotExist:
            return None


class PasswordResetForm(SetPasswordForm):
    """ Form for setting new password """
    error_messages = {
        'password_mismatch': 'The passwords entered did not match.',
    }


class PasswordUpdateForm(PasswordChangeForm):
    """ Form for setting new password """
    error_messages = {
        'password_incorrect': 'Your old password was entered incorrectly.',
        'password_mismatch': 'The passwords entered did not match.',
    }


class EmailForm(forms.ModelForm):
    """ Form for representing an email """
    class Meta:
        model = Email
        fields = '__all__'

    def save(self, commit=True):
        email = super().save(commit=False)
        # save if new email
        if not Email.objects.filter(user=email.user, email_address=email.email_address):
            if commit:
                email.save()
                return email
        return None
