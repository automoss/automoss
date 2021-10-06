from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.template.loader import render_to_string
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager
)
from django.contrib.auth.validators import (
    UnicodeUsernameValidator
)
import uuid
from .tasks import send_emails
from ...settings import (
    UUID_LENGTH,
)


class UserManager(BaseUserManager):
    """ Manager for custom user class

        Based on Django's implementation and example found at:
        https://www.codingforentrepreneurs.com/blog/how-to-create-a-custom-django-user-model
    """
    use_in_migrations = True

    def _create_user(self, course_code, primary_email_address, moss_id, password, **extra_fields):
        """
        Create and save a user with the given course code, primary email, MOSS ID and password.
        """
        if not course_code:
            raise ValueError('The given username must be set')
        if not primary_email_address:
            raise ValueError('The given primary email must be set')
        if not moss_id:
            raise ValueError('The given MOSS ID must be set')
        normalized_email = self.normalize_email(primary_email_address)
        user = self.model(
            course_code=course_code,
            primary_email_address=normalized_email,
            moss_id=moss_id,
            **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, course_code, primary_email_address, moss_id, password=None, **extra_fields):
        """
        Creates and saves user with no admin level permissions by default.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(
            course_code,
            primary_email_address,
            moss_id,
            password,
            **extra_fields
        )

    def create_staffuser(self, course_code, primary_email_address, moss_id, password=None, **extra_fields):
        """
        Creates and saves a staff user.
        """
        extra_fields.setdefault('is_staff', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Staffuser must have is_staff=True.')

        return self._create_user(
            course_code,
            primary_email_address,
            moss_id, password,
            **extra_fields
        )

    def create_superuser(self, course_code, primary_email_address, moss_id, password=None, **extra_fields):
        """
        Creates and saves a super user.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(
            course_code,
            primary_email_address,
            moss_id,
            password,
            **extra_fields
        )


class User(AbstractBaseUser):
    """
    A fully-featured User model with admin-compliant permissions.

    Based on Django's implementation
    """

    # Allow Unicode course codes
    course_code_validator = UnicodeUsernameValidator()

    # Unique identifier used in routing
    user_id = models.CharField(
        primary_key=False,
        default=uuid.uuid4,
        max_length=UUID_LENGTH,
        editable=False,
        unique=True
    )

    # Course Code will be the username
    course_code = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        validators=[course_code_validator],
        error_messages={
            'unique': "A user with that username already exists."
        })

    # Email to send administritive content to
    primary_email_address = models.EmailField(
        blank=False,
        null=False
    )

    # Account/Email verified
    is_verified = models.BooleanField(
        default=False
    )

    # MOSS ID for using the MOSS API
    moss_id = models.CharField(
        unique=True,
        max_length=32,
        blank=False,
        null=False
    )

    # User with admin permissions
    is_staff = models.BooleanField(
        default=False
    )

    # Superuser with all permissions
    is_superuser = models.BooleanField(
        default=False
    )

    # Is active account
    is_active = models.BooleanField(
        default=True,
    )

    # Date user account created
    date_joined = models.DateTimeField(
        default=now
    )

    objects = UserManager()

    EMAIL_FIELD = 'primary_email_address'
    USERNAME_FIELD = 'course_code'
    REQUIRED_FIELDS = [EMAIL_FIELD, "moss_id"]

    def clean(self):
        super().clean()
        self.primary_email_address = self.__class__.objects.normalize_email(
            self.primary_email_address)

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

    def send_email(self, subject_template, body_template, html_template, context, broadcast=False):
        """Send an email to this user and possibly associated emails if broadcast email """

        # Render templates
        subject = render_to_string(subject_template, context).strip()
        body = render_to_string(body_template, context)
        html = render_to_string(html_template, context)
        recipients = [str(self.primary_email_address)]

        # Add to recipient list if broadcast
        if broadcast:
            recipients += [str(email)
                           for email in self.email_set.filter(is_verified=True)]

        # Send emails asynchronously
        send_emails.apply_async(kwargs={
            'from_email': settings.DEFAULT_FROM_EMAIL,
            'recipients': recipients,
            'subject': subject,
            'body': body,
            'html': html
        }, queue='email')

    def __str__(self):
        """ User to string returns course code """
        return self.course_code


class Email(models.Model):
    """ Secondary email address associated with a user account """

    # User foreign key - an email belongs to a user
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Unique ID for use in URLs
    email_id = models.CharField(
        primary_key=False,
        default=uuid.uuid4,
        max_length=UUID_LENGTH,
        editable=False,
        unique=True
    )

    # Email address
    email_address = models.EmailField(
        blank=False,
        null=False
    )

    # Email verified
    is_verified = models.BooleanField(
        default=False
    )

    def send_email(self, subject_template, body_template, html_template, context):
        """Send an email to this email """

        # Render templates
        subject = render_to_string(subject_template, context).strip()
        body = render_to_string(body_template, context)
        html = render_to_string(html_template, context)
        recipients = [str(self.email_address)]

        # Send emails asynchronously
        send_emails.apply_async(kwargs={
            'from_email': settings.DEFAULT_FROM_EMAIL,
            'recipients': recipients,
            'subject': subject,
            'body': body,
            'html': html
        }, queue='email')

    def __str__(self):
        """ Email to string """
        return self.email_address
