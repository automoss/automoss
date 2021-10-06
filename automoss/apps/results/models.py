from django.utils.timezone import now
from django.db import models
from ...settings import UUID_LENGTH, COMPLETED_STATUS
import uuid
from ..jobs.models import Job, Submission


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


class MatchManager(models.Manager):
    """ Custom Match manager """

    def user_matches(self, user):
        """ Returns set of matches belonging to user """
        return self.get_queryset().filter(moss_result__job__user=user)


class Match(models.Model):
    """ Class to model MOSS Match """

    # Custom manager
    objects = MatchManager()

    # ID of the match
    match_id = models.CharField(
        primary_key=False,
        default=uuid.uuid4,
        max_length=UUID_LENGTH,
        editable=False,
        unique=True
    )

    # MOSS result of the job
    moss_result = models.ForeignKey(MOSSResult, on_delete=models.CASCADE)

    # Submissions the match compares
    first_submission = models.ForeignKey(
        Submission, related_name='first_submission', on_delete=models.CASCADE)
    second_submission = models.ForeignKey(
        Submission, related_name='second_submission', on_delete=models.CASCADE)

    # Match percentages
    first_percentage = models.IntegerField()
    second_percentage = models.IntegerField()

    # Line match information
    lines_matched = models.IntegerField()
    line_matches = models.JSONField()

    def __str__(self):
        """ Match to string method """
        return f'{self.first_submission} - {self.second_submission}'
