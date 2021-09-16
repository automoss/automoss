from ...settings import SUBMISSION_TYPES
import uuid
from django.utils.timezone import now
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

from ...settings import (
    STATUSES,
    SUPPORTED_LANGUAGES,
    DEFAULT_MOSS_SETTINGS,
    UUID_LENGTH,
    MAX_COMMENT_LENGTH
)
from ...apps.utils.core import (to_choices, get_longest_key, first)


def get_default_comment():
    """ Returns default job comment """
    return f"My Job - {now().strftime('%d/%m/%y-%H:%M:%S')}"

User = get_user_model()

class Job(models.Model):
    """ Class to model Job Entity """
    # MOSS user that created the job
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Unique identifier used in routing
    job_id = models.CharField(
        primary_key=False,
        default=uuid.uuid4,
        max_length=UUID_LENGTH,
        editable=False,
        unique=True
    )

    # Language choice
    language = models.CharField(
        max_length=get_longest_key(SUPPORTED_LANGUAGES),
        choices=[(l, SUPPORTED_LANGUAGES[l][0]) for l in SUPPORTED_LANGUAGES],
        default=first(SUPPORTED_LANGUAGES),
    )

    # Max matches of a code segment before it is ignored
    max_until_ignored = models.PositiveIntegerField(
        default=DEFAULT_MOSS_SETTINGS['max_until_ignored'])
    # Max displayed matches
    max_displayed_matches = models.PositiveIntegerField(
        default=DEFAULT_MOSS_SETTINGS['max_displayed_matches'])
    # Comment/description attached to job
    comment = models.CharField(
        max_length=MAX_COMMENT_LENGTH, default=get_default_comment)

    # Job status
    status = models.CharField(
        max_length=get_longest_key(STATUSES),
        choices=to_choices(STATUSES),
        default=first(STATUSES),
    )
    # Date and time job was created
    creation_date = models.DateTimeField(default=now)

    # Date and time job was started
    start_date = models.DateTimeField(null=True, blank=True)

    # Date and time job was completed
    completion_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        """ Model to string method """
        return f"{self.comment} ({self.job_id})"


class Submission(models.Model):
    """ Class to model MOSS Report Entity """
    # Job submission belongs to
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    # Unique identifier used in routing
    submission_id = models.CharField(
        primary_key=False,
        default=uuid.uuid4,
        max_length=UUID_LENGTH,
        editable=False,
        unique=True
    )

    # Name of the submission
    name = models.CharField(max_length=64)

    file_type = models.CharField(
        max_length=get_longest_key(SUBMISSION_TYPES),
        choices=to_choices(SUBMISSION_TYPES)
    )

    def __str__(self):
        return f'{self.submission_id} ({self.name})'
