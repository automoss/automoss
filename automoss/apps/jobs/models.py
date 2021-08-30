import uuid
from django.utils.timezone import now
from django.db import models
from ..users.models import MOSSUser

from ...defaults import (
    MAX_STATUS_LENGTH,
    STATUS_CHOICES,
    DEFAULT_STATUS,
    MAX_UNTIL_IGNORED,
    MAX_DISPLAYED_MATCHES,
    MAX_LANGUAGE_LENGTH,
    LANGUAGE_CHOICES,
    DEFAULT_LANGUAGE,
    MAX_COMMENT_LENGTH,
    UUID_LENGTH,
    SUBMISSION_TYPE_CHOICES,
    MAX_SUBMISSION_TYPE_LENGTH
)


def get_default_comment():
    """ Returns default job comment """
    return f"My Job - {now().strftime('%d/%m/%y-%H:%M:%S')}"


class Job(models.Model):
    """ Class to model Job Entity """
    # MOSS user that created the job
    moss_user = models.ForeignKey(MOSSUser, on_delete=models.CASCADE)
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
        max_length=MAX_LANGUAGE_LENGTH,
        choices=LANGUAGE_CHOICES,
        default=DEFAULT_LANGUAGE,
    )

    # Max matches of a code segment before it is ignored
    max_until_ignored = models.PositiveIntegerField(default=MAX_UNTIL_IGNORED)
    # Max displayed matches
    max_displayed_matches = models.PositiveIntegerField(
        default=MAX_DISPLAYED_MATCHES)
    # Comment/description attached to job
    comment = models.CharField(
        max_length=MAX_COMMENT_LENGTH, default=get_default_comment)

    # Job status
    status = models.CharField(
        max_length=MAX_STATUS_LENGTH,
        choices=STATUS_CHOICES,
        default=DEFAULT_STATUS,
    )
    # Date and time job was started
    start_date = models.DateTimeField(default=now)
    # Date and time job was completed
    completion_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        """ Model to string method """
        return f"{self.comment} ({self.job_id})"


class Submission(models.Model):
    """ Class to model MOSS Report Entity """
    # Job submission belongs to
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    # Name/ID of the submission
    name = models.CharField(max_length=64)

    file_type = models.CharField(
        max_length=MAX_SUBMISSION_TYPE_LENGTH, choices=SUBMISSION_TYPE_CHOICES)

    def __str__(self):
        return f'{self.name} ({self.job.job_id})'
