import uuid
from django.utils.timezone import now
from django.db import models

def get_default_comment():
    """ Returns default job comment """
    return f"My Job - {now().strftime('%d/%m/%y-%H:%M:%S')}"

# Job Model
class Job(models.Model):
    """ Class to model Job Entity
    """
    # Unique identifier used in routing
    job_id = models.CharField(primary_key=False, default=uuid.uuid4, max_length=32, editable=False, unique=True)
    # Language choice
    LANGUAGES = [("CX", "C"), ("CP", "C++"), ("JA", "Java"), ("CS", "C#"), ("PY", "Python"), ("JS", "Javascript"), ("PL", "Perl"), ("MP", "MIPS")]
    language = models.CharField(
        max_length=2,
        choices=LANGUAGES,
        default=LANGUAGES[4][0],
    )
    # Max matches of a code segment before it is ignored
    max_until_ignored = models.PositiveIntegerField(default=1000000)
    # Max displayed matches
    max_displayed_matches = models.PositiveIntegerField(default=1000000)
    # Comment/description attached to job
    comment = models.CharField(max_length=64, default=get_default_comment)
    # Job status
    STATUSES = [("UPL", "Uploading"), ("PRO", "Processing"), ("COM", "Complete"), ("FAI", "Failed")]
    status = models.CharField(
        max_length=3,
        choices=STATUSES,
        default=STATUSES[0][0],
    )
    # Date and time job was started
    start_date = models.DateTimeField(default=now)
    # Date and time job was completed
    completion_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        """ Model to string method
        """
        return f"{self.comment} ({self.job_id})"

