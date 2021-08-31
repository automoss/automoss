from ...settings import SUBMISSION_TYPES
from ...settings import COMPLETED_STATUS
import uuid
from django.utils.timezone import now
from django.db import models
from ..users.models import MOSSUser

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
        max_length=get_longest_key(SUBMISSION_TYPES),
        choices=to_choices(SUBMISSION_TYPES)
    )

    def __str__(self):
        return f'{self.name} ({self.job.job_id})'


class MOSSResult(models.Model):
    """ Class to model MOSS Result Entity """
    # Job result belongs to
    job = models.OneToOneField(Job, on_delete=models.CASCADE, limit_choices_to={
                               'status': COMPLETED_STATUS})
    # Date result was created
    created_date = models.DateTimeField(default=now)

    # MOSS URL of result
    url = models.URLField(default=None)

    def __str__(self):
        """ Report to string method """
        return f"Report at {self.url}"


class Match(models.Model):
    """ Class to model MOSS Match """

    match_id = models.CharField(
        primary_key=False,
        default=uuid.uuid4,
        max_length=UUID_LENGTH,
        editable=False,
        unique=True
    )

    moss_result = models.ForeignKey(MOSSResult, on_delete=models.CASCADE)

    # Submissions the match compares
    first_submission = models.ForeignKey(
        Submission, related_name='first_submission', on_delete=models.CASCADE)
    second_submission = models.ForeignKey(
        Submission, related_name='second_submission', on_delete=models.CASCADE)

    first_percentage = models.IntegerField()
    second_percentage = models.IntegerField()

    lines_matched = models.IntegerField()
    line_matches = models.JSONField()

    def __str__(self):
        return f'{self.first_submission} - {self.second_submission}'
