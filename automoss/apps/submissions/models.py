from django.db import models
from ..jobs.models import Job
from ...apps.utils.core import (to_choices, get_longest_key,)
from ...settings import SUBMISSION_TYPES

# Create your models here.
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
