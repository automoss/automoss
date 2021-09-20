import unicodedata
from .models import User
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from ..moss.moss import MOSS

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
            valid_id = MOSS().validate_moss_id(clean_moss_id, raise_if_connection_error=True)
        except ConnectionError as ce:
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

class LoginForm(AuthenticationForm):
    """ User login form """
    error_messages = {
        'invalid_login': 'The course code and password entered were incorrect.',
        'inactive': 'That account is diabled.',
    }
