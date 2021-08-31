import uuid
from django.utils.timezone import now, timedelta
from django.db import models
from ..jobs.models import Job
from ..submissions.models import Submission


class Match(models.Model):
    """ Class to model MOSS Match """
    # Submissions the match compares
    first_submission = models.ForeignKey(Submission, related_name='first_submission', on_delete=models.CASCADE)
    second_submission = models.ForeignKey(Submission, related_name='second_submission', on_delete=models.CASCADE)

    first_percentage = models.IntegerField()
    second_percentage = models.IntegerField()

    lines_matched = models.IntegerField()
    line_matches = models.JSONField()

    def __str__(self):
        return f'{self.first_submission} - {self.second_submission}'
